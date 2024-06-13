import streamlit as st
from openai import OpenAI
from newsfetcher import NewsFetcher
import json
import prompts
import datetime
import random

client = OpenAI()

st.set_page_config(
    page_title="Summarization with LLMs",
    page_icon=":bar_chart:",
    layout="wide",
)

example_topics = [
    "Microsoft OpenAI Partnership",
    "Federal Reserve Interest Rate Decision",
    "Taylor Swift Relationship Status",
]

def get_response(messages, model='gpt-4o'):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

def get_response_stream(messages, model='gpt-4o'):
    response = ""
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content
            yield chunk.choices[0].delta.content  # Yield the content directly for streaming
    return response

def articles_to_string(articles_df, include_id=True, include_name=True, include_date=True, include_url=True, include_text=True):
    articles_info = []
    for index, row in articles_df.iterrows():
        parts = []
        if include_id:
            parts.append(f"**Article ID:** {index}\n\n")
        if include_name:
            parts.append(f"**{row['name']}**\n\n")
        if include_date:
            parts.append(f"**Article Date:** {str(row['datePublished'])}\n\n")
        if include_url:
            parts.append(f"**Article URL:** {row['url']}\n\n")
        if include_text:
            parts.append(f"**Article Text:** {row['text']}\n\n")
        
        article_string = "".join(parts)
        articles_info.append(article_string)

    return "\n\n".join(articles_info)

@st.cache_data(show_spinner=False)
def get_articles_df(ticker):
    newsfetcher = NewsFetcher(ticker, 100)
    newsfetcher.run()
    return newsfetcher.articles_df

@st.cache_data(show_spinner=False)
def get_seed():
    return random.randint(0, len(example_topics) - 1)

st.title("Summarization with LLMs")

st.caption("A benefit of Large Language Models (LLMs) is their ability to sift through vast amounts of unstructured data.")

st.markdown("> 1. Summarization can be broadly defined as an optimization problem in which the goal is to identify, extract, and condense **important information** from a larger body of content.  \n> 2. For a summary to have value, this process must be **interpretable**.")

st.divider()

topic = st.text_input("Enter a recent news topic or use the example:", f"{example_topics[get_seed()]}")
if not st.button("Start"):
    st.stop()
    
with st.spinner(f"Fetching articles for **{topic}**..."):
    articles_df = get_articles_df(topic)
    articles_df = articles_df[articles_df['text'] != '']
    articles_df = articles_df.sample(min(25, len(articles_df))).reset_index(drop=True)
st.success(f"Fetched {len(articles_df)} articles for {topic}.")

st.divider()


st.subheader("Single Article Summarization")

st.info("As a baseline, let's start with some simple examples of generic single-article summaries for the specified topic.")

st.code("""
system_prompt = \"\"\"\nYou provide clear and concise summaries of news articles. It is crucial that you escape all dollar signs with a backslash: \$.\n\"\"\"
user_prompt = \"\"\"\n{articles_to_string(articles_df.iloc[0:1])}\n\"\"\"
""")

col1, col2, col3 = st.columns(3)

model = "gpt-4o"

with col1.expander("Single Article Summarization - Article 1", expanded=True):
    article = articles_df.iloc[0:1]
    st.page_link(page=article['url'].values[0], label="View Article")
    with st.container(height=400):
        messages = [{"role": "system", "content": f"You provide clear and concise summaries of news articles. It is crucial that you escape all dollar signs with a backslash: \$. Todays date is {datetime.datetime.now().strftime('%Y-%m-%d')}"}, {"role": "user", "content": articles_to_string(article)}]
        summary_1 = st.write_stream(get_response_stream(messages, model))

with col2.expander("Single Article Summarization - Article 2", expanded=True):
    article = articles_df.iloc[1:2]
    st.page_link(page=article['url'].values[0], label="View Article")
    with st.container(height=400):
        messages = [{"role": "system", "content": f"You provide clear and concise summaries of news articles. It is crucial that you escape all dollar signs with a backslash: \$. Todays date is {datetime.datetime.now().strftime('%Y-%m-%d')}"}, {"role": "user", "content": articles_to_string(article)}]
        summary_2 = st.write_stream(get_response_stream(messages, model))

with col3.expander("Single Article Summarization - Article 3", expanded=True):
    article = articles_df.iloc[2:3]
    st.page_link(page=article['url'].values[0], label="View Article")
    with st.container(height=400):
        messages = [{"role": "system", "content": f"You provide clear and concise summaries of news articles. It is crucial that you escape all dollar signs with a backslash: \$. Todays date is {datetime.datetime.now().strftime('%Y-%m-%d')}"}, {"role": "user", "content": articles_to_string(article)}]
        summary_3 = st.write_stream(get_response_stream(messages, model))
        
st.success("Great! We've established that we can generate clearer and more concise representations of the information in the articles. We can call these ***compactness-oriented summaries***, since their purpose is simply to present a distilled version of the content. This is generally what people refer to by 'summarization.'")

st.warning("**However, for a variety of reasons, this isn't really more valuable than just skimming the article yourself:**  \n - Most of the value in skimming does not come from looking at one article: it comes drawing cross-article inferences.\n - We can't really be sure about what information was lost during the summarization process; when skimming, the information you focus on in each successive article will be influenced by the previous articles, allowing you to make more meaningful decisions about what to keep and discard.\n     - Since each summary is independent, there is no reason to believe the details kept during summarization would be correlated across articles.\n\n")

st.divider()

st.subheader("News Cycle Summarization")

st.info("One potential solution to these problems is to include multiple articles (such as a sample from the recent news cycle) in the same prompt. This feels like it would be more useful than summarizing single articles, since we can ask the model to help draw connections between them. We'll also ask it to cite sources inline for traceability.")

st.code(f"""
system_prompt = \"\"\"\n{prompts.cycle_system_prompt}\n\"\"\"
user_prompt = \"\"\"\n{{articles_to_string(articles_df)}}\n\nEnsure you reference source URLs in the summaries using inline Markdown with footnote references, such as [^1^].\n\"\"\"
""")

with st.expander("News Cycle Summarization", expanded=True):
    with st.container(height=500):
        messages = [{"role": "system", "content": prompts.cycle_system_prompt}, {"role": "user", "content": articles_to_string(articles_df) + f"\n\nEnsure you reference source URLs in the summaries using inline Markdown with footnote references, such as [^1^]. Todays date is {datetime.datetime.now().strftime('%Y-%m-%d')}"}]
        cycle_summary_1 = st.write_stream(get_response_stream(messages, model))
        
st.success("The breadth certainly makes this more useful than a few single-article summaries!")

st.warning("This is a good starting point, but we can do better:\n - If you retrieved more than 20 articles, the model probably didn't reference all of the sources.\n - We also have no idea why it made the decisions it did around the inclusion/exclusion of information.\n - We could ask the model to explain its reasoning *ex post*, and it would likely generate a plausible explanation, but this approach has numerous limitations and requires several logical assumptions to interpret.")


st.divider()


st.subheader("Compression for Summarization")

st.info("Instead, let's try a different approach, somewhat similar to the one used in [RECOMP](https://arxiv.org/pdf/2310.04408) (**Re**trieve, **Co**mpress, **P**repend). We're not really focused on optimizing our search in this post, so our objective in this section will be to create a flow incorporating compression and prepension that yields a summary unlikely to be missing relevant information. We will also be incorporating some of our observations from the examples above to form a more meaningful summary.")

st.info("**We're going to need an objective to organize our compression.**  \nOne way you might do this manually would be to skim the headlines and write down a few questions you'd like to answer. While we'll have the model do this, you could always come up with these yourself. Then, we can leverage these questions by asking the model to answer them in the summary: this will help us decrease the likelihood of losing important information relevant to our questions.")

st.caption("*The prompts at this stage are multi-step and a bit longer, but still relatively simple. Please reference the GitHub repository for the full code if you'd like to view them.*")


col1, col2 = st.columns([1, 2])

messages = [{"role": "system", "content": f"Topic: {topic}\n\nTodays date is {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n{prompts.questioning_system_prompt}"}, {"role": "user", "content": f"Articles:\n{articles_to_string(articles_df)}\n\nPlease provide up to 6 open-ended questions that can be used to encourage critical thinking about the news cycle."}]

questions = get_response(messages, model)
            
with col1.container(height=600):
    for i, question in enumerate(questions['questions'], start=1):
        with st.expander(f"Question {i}", expanded=False):
            st.write(question)

analysis_messages = [{"role": "system", "content": f"Topic: {topic}\n\nTodays date is {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n{prompts.analyzing_system_prompt}"}, {"role": "user", "content": f"Articles:\n{articles_to_string(articles_df)}\n\nQuestions:\n{json.dumps(questions)}"}]


with col2.container(height=600):
    analysis = st.write_stream(get_response_stream(analysis_messages, model))
    
st.success("Compare this summary to the ones above. By incorporating the questions, we've given the task a purpose and created a more meaningful summary that is less likely to miss the information we want.")

st.warning("This is a good example of how we can use LLMs to sift through large amounts of unstructured data, but how can we continue to expand this structure? How can we use this pattern to help make decisions?")

st.divider()

st.subheader("Adding Layers")

st.info("One potential application of this pattern is to use it to directionally update likelihood judgements: this is a simplistic example of feature extraction. We'll use the model to generate the hypothesis here, as well as a likelihood, but again, you could always come up with this yourself to test your own biases. After that, we'll generate a series of questions and use them to test the hypothesis before answering them in the summary.")

st.caption("*The prompts at this stage are multi-step and a bit longer, but still relatively simple. Please reference the GitHub repository for the full code if you'd like to view them.*")

col1, col2, col3 = st.columns([1,1,2])

messages = [
    {
        "role": "system",
        "content": f"You provide a hypothesis and associated likelihood for news cycle analysis for the topic '{topic}'. It is crucial that you escape all dollar signs with a backslash: \$. Todays date is {datetime.datetime.now().strftime('%Y-%m-%d')}"
    },
    {
        "role": "user",
        "content": f"The hypothesis should be a clear, specific, and falsifiable statement that addresses a single, measurable outcome within a defined time frame. It is absolutely imperative that the hypothesis possesses a sufficient level of granularity as to be falsifiable. The likelihood should be a string representation of a either 1, 2, or 3 (where 1 indicates a probability (0%, 50%], 2:(50%, 85%] and 3:(85%:100%)) that reflects your confidence level, is supported by prior knowledge, and is testable with recent information. Namely, we will be testing via the following articles:\n{articles_to_string(articles_df, include_id=False, include_name=True, include_url=False, include_text=True)}\nPlease provide a hypothesis and an initial likelihood in the following JSON format: {{\"hypothesis\": \"Your hypothesis here.\", \"probability\": \"Likelihood level (1,2,3) here\", \"rationale\": \"Short rationale here.\"}}"
    }
]


with col1.container(height=600):
    with st.spinner("Generating hypothesis..."):
        hypothesis = get_response(messages, model)
    with st.expander("Hypothesis", expanded=True):
        st.write(hypothesis['hypothesis'])
    with st.expander("Initial Likelihood", expanded=True):
        st.metric(label="Likelihood", value=int(hypothesis['probability']), help="1: Low likelihood (0% to 49%)\n\n2: Moderate likelihood (50% to 84%)\n\n3: High likelihood (85% to 100%)")
    with st.expander("Rationale", expanded=True):
        st.write(hypothesis['rationale'])      

messages = [
    {
        "role": "system",
        "content": f"Topic: {topic}\n\n{prompts.questioning_hypothesis_system_prompt}. Todays date is {datetime.datetime.now().strftime('%Y-%m-%d')}"
    },
    {
        "role": "user",
        "content": f"Articles:\n{articles_to_string(articles_df, include_id=False, include_name=True, include_url=False, include_text=True)}\n\nPlease provide up to 6 open-ended questions that can be used to test the hypothesis."
    }
]
with col2.container(height=600):
    with st.spinner("Generating questions..."):
        questions = get_response(messages, model)
        for i, question in enumerate(questions['questions'], start=1):
            with st.expander(f"Question {i}", expanded=True):
                st.write(question)
            
messages = [
    {
        "role": "system",
        "content": f"Topic: {topic}\n\n{prompts.analyzing_questions_system_prompt}. Todays date is {datetime.datetime.now().strftime('%Y-%m-%d')}"
    },
    {
        "role": "user",
        "content": f"Articles:\n{articles_to_string(articles_df, include_id=False, include_name=True, include_url=False, include_text=True)}\n\nHypothesis:\n{json.dumps(hypothesis['hypothesis'])}\n\nQuestions:\n{json.dumps(questions)}"
    }
]

with col3.container(height=600):
    analysis = st.write_stream(get_response_stream(messages, model))
    
messages = [
    {
        "role": "system",
        "content": f"Topic: {topic}\n\n{prompts.hypothesis_final_system_prompt}. Todays date is {datetime.datetime.now().strftime('%Y-%m-%d')}"
    },
    {
        "role": "user",
        "content": f"Articles:\n{articles_to_string(articles_df, include_id=False, include_name=True, include_url=False, include_text=True)}\n\nHypothesis:\n{json.dumps(hypothesis['hypothesis'])}\n\Likelihood\n{json.dumps(hypothesis['probability'])}\n\Analysis:\n{analysis}\nThe final probability should reflect your confidence level after considering the analysis; it should be supported by the information in the articles and the analysis. Please evaluate the hypothesis and provide a final probability and rationale in the following JSON format: {{\"likelihood\": \"Final likelihood level (1,2,3) here\", \"rationale\": \"Short rationale here.\", \"further_research\": \"Alternative sources for further research here.\"}}\n Format your response for readability, with no headers larger than H5 (#####)."
    }
]

with st.expander("Final Analysis", expanded=True):
    with st.spinner("Generating final analysis..."):
        final_analysis = get_response(messages, model)
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 2])
            
            col1.caption("Updated Likelihood")
            col1.metric(label="Likelihood", value=int(final_analysis['likelihood']), delta=(int(final_analysis['likelihood']) - int(hypothesis['probability'])), help="1: Low likelihood (0% to 49%)\n\n2: Moderate likelihood (50% to 84%)\n\n3: High likelihood (85% to 100%)")
            
            col2.caption("Updated Rationale")
            col2.write(final_analysis['rationale'])
            
            col3.caption("Areas for Further Research")
            col3.write(final_analysis['further_research'])

st.success("Although this example is simplistic in order to be generally applicable, we've clearly demonstrated how LLMs can be used for tasks like summarization and feature extraction. Its easy to see how, with further development, this pattern could be expanded on and would scale well to evaluate large quantities of loosely structured data in a variety of domains. The real value here probably isn't in the feature extraction, but rather in the idea generation and contextualization of information.")

st.warning("""**There are some limitations to consider:**
- The model is heavily reliant on the quality and breadth of the input data to contextualize the value of individual pieces of information, and neither is a guarantee here.
- The feature extraction example will almost never update the likelihood in a meaningful way since it uses the same data in each iteration.
    - If it does, **pay attention**, because the model likely picked up on something nuanced.
    - A more interesting approach might be to run this process two weeks apart for the same hypothesis.
           
**Some of the obvious first steps to improve this process would be to:**
- Pre-filter articles for relevance to the specific hypothesis before forming questions so that the model isn't distracted by irrelevant information.
- Use a wider range of data sources than a single news aggregator.
- Focus the process on a specific use-case, such as monitoring an investment thesis or continuously verifying a medical diagnosis, to achieve more meaningful results.""")

st.divider()