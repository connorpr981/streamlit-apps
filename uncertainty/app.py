import streamlit as st
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
import json
from vertexai.generative_models import GenerativeModel
from concurrent.futures import ThreadPoolExecutor
import vertexai
import re
from tqdm import tqdm

st.set_page_config(layout="wide")

st.title("Intelligence")

quote = """
> *"Intelligence is prediction, pointed with intention." 
> <a href="https://x.com/eshear/status/1798533593272307962" target="_blank"><sup>1</sup></a>*
"""
st.markdown(quote, unsafe_allow_html=True)

PROJECT_ID = "sharp-airway-408502"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel(model_name="gemini-1.5-pro-001")

with open("test.txt", "r") as f:
    content = f.read()

# Assuming df is already defined as per your provided code
# Define the regex pattern
pattern = re.compile(r'(\w+\s\w+)\s(\d{2}:\d{2}:\d{2})\n([\s\S]+?)(?=\n\w+\s\w+\s\d{2}:\d{2}:\d{2}|$)')

# Extract matches from the content
matches = pattern.findall(content)

# Create a list of dictionaries with speaker, start time, and text
transcript_entries = [{'speaker': match[0], 'start_time': match[1], 'text': match[2].strip()} for match in matches]

df = pd.DataFrame(transcript_entries)

# Identify the second speaker
second_speaker = 'Leopold Aschenbrenner'

# Initialize chunks list
chunks = []

# Loop through the dataframe
i = 0
while i < len(df):
    if df.loc[i, 'speaker'] == second_speaker:
        # Capture the preceding statements by the first speaker
        preceding_statements = []
        j = i - 1
        while j >= 0 and df.loc[j, 'speaker'] != second_speaker:
            preceding_statements.insert(0, f"{df.loc[j, 'speaker']}\n{df.loc[j, 'text']}")
            j -= 1
        
        # Capture the second speaker's statement
        second_speaker_statements = []
        while i < len(df) and df.loc[i, 'speaker'] == second_speaker:
            second_speaker_statements.append(f"{df.loc[i, 'speaker']}\n{df.loc[i, 'text']}")
            i += 1
        
        # Capture the subsequent statements by the first speaker
        following_statements = []
        while i < len(df) and df.loc[i, 'speaker'] != second_speaker:
            following_statements.append(f"{df.loc[i, 'speaker']}\n{df.loc[i, 'text']}")
            i += 1
        
        # Combine all statements into one chunk
        chunk = "\n".join(preceding_statements + second_speaker_statements + following_statements)
        chunks.append(chunk)
    else:
        i += 1

results_df = pd.DataFrame(chunks, columns=['text'])

constant_prompt = '''You will have access to an excerpt from podcast transcription where Dwarkesh Patel interviews Leopold Aschenbrenner.

Your task is to extract the beliefs explicitly expressed by Leopold Aschenbrenner in the interview:
 - You should not include beliefs that are implied or inferred.
 - You should not include beliefs that are expressed by Dwarkesh Patel.

The beliefs should be extracted as a list of dictionary objects, where each dictionary object has the following keys: "belief", "context", "justification", and "certainty":
 - The "belief" key should contain the belief that was expressed by Leopold Aschenbrenner.
 - The "context" key should contain the exact text where the belief was expressed. This should help illustrate the circumstances under which the belief was expressed.
 - The "justification" key should contain the key supporting evidence for the belief expressed during the interview. 
 - The "certainty" key should contain either "high", "medium", or "low" to indicate the confidence level expressed in the belief by Leopold Aschenbrenner.

Please provide your response in the form of a compilable JSON object. For example:
```json
{
    "beliefs": [
        {
            "belief": "The sky is blue.",
            "context": "The person is talking about the color of the sky.",
            "justification": "The sky is blue because it is the color that we see when we look up.",
            "certainty": "high",
        },
        {
            "belief": "The sun is hot.",
            "context": "The person is talking about the temperature of the sun.",
            "justification": "The sun is hot because it emits heat and light.",
            "certainty": "medium"
        }
        ...
    ]
}
```

Here is the excerpt from the podcast transcription:
<excerpt>
'''

# Define a retrying function with exponential backoff
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
def process_chunk(text):
    prompt = constant_prompt.replace("<excerpt>", text)
    try:
        response = model.generate_content(contents=prompt, generation_config={"response_mime_type": "application/json"})
        response_json = json.loads(response.text)
        beliefs = response_json['beliefs']
        return json.dumps(beliefs)
    except json.JSONDecodeError as e:
        # Raise an exception to trigger retry
        raise ValueError("JSON decoding error, triggering retry") from e
    except ValueError as e:
        # Handle specific ValueError related to blocked content
        return f"Error: {str(e)}"
    except Exception as e:
        # Handle other potential errors
        return f"Unexpected Error: {str(e)}"

# Use ThreadPoolExecutor for multithreading with tqdm progress bar
with ThreadPoolExecutor(max_workers=100) as executor:  # limiting max_workers to a reasonable number
    extracted_beliefs = list(tqdm(executor.map(process_chunk, results_df['text']), total=len(results_df)))

# Add the extracted beliefs to the DataFrame
results_df['extracted_beliefs'] = extracted_beliefs

for i, item, in results_df['extracted_beliefs'].items():
    try:
        beliefs = json.loads(item)
        for belief in beliefs:
            st.write(f"Chunk {i + 1}")
            st.json(belief)
    except json.JSONDecodeError as e:
        st.write(f"Error decoding JSON for Chunk {i + 1}: {str(e)}")