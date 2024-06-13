system_message = """TODAY'S DATE: <date>
PODCAST AIR DATE: <air_date>
GUEST: <guest>
HOST: <host>

It is imperative that you adhere to the output format specified by the user, including the types of variables and the order in which they are presented.
"""

belief_extraction = '''You will have access to an excerpt from a podcast transcription where <host> interviews <guest>.

Your task is to extract the beliefs explicitly expressed by <guest> in the interview. The purpose of this task is to identify and categorize beliefs for further evaluation to understand their justifiability. Do not include beliefs that are implied or inferred, nor beliefs expressed by <host>.

Please follow this decision tree for each statement made by <guest> in THE EXCERPT:

1. Is the statement a belief explicitly expressed by <guest>?
   - If yes, proceed to step 2.
   - If no, disregard the statement and move on to the next one.

2. Is the belief implied, inferred, or expressed by <host>?
   - If yes, disregard the belief and move on to the next statement.
   - If no, proceed to step 3.

3. Identify the type of belief expressed:
   - Is it based on observable, measurable evidence or scientific data, obtained through systematic observation or experimentation? If yes, categorize it as "empirical".
   - Is it derived from logical reasoning, deduction, or induction, based on the available evidence or premises? If yes, categorize it as "rational".
   - Is it based on personal experiences, observations, or anecdotes, which are subjective and not necessarily generalizable? If yes, categorize it as "experiential".
   - Is it a belief about values, ethics, or normative principles, dealing with how things ought to be or what is considered good or right? If yes, categorize it as "axiological".
   - Is it a belief about the nature of reality, existence, being, or knowledge itself, which are often not directly verifiable through empirical means? If yes, categorize it as "metaphysical".

4. Extract the following details for the belief:
   - Belief: (string) A detailed and precise statement of the belief expressed by <guest>.
   - Type: (string) The type of belief identified in step 3.
   - Context: (string) A description of the broader context and intent behind stating the belief within the conversation.
   - Justification: (string) The key supporting evidence for the belief expressed during the interview, including any data, reasoning, experiences, or principles mentioned.
   - Confidence: (string) The confidence level expressed in the belief by <guest> ("high", "medium", or "low").

5. Add the extracted belief and its details to the list of extracted beliefs.

6. Move on to the next statement in THE EXCERPT and repeat steps 1-5 until all statements have been processed.

Please provide your response in the form of a compilable JSON object with the following structure:
[
    {
        "belief": "The universe began with a rapid expansion from a singularity, known as the Big Bang, approximately 13.8 billion years ago.",
        "type": "empirical",
        "context": "The discussion was about the origin and evolution of the universe, and <guest> presented the Big Bang theory as the most widely accepted scientific explanation.",
        "justification": "The Big Bang theory is supported by observable evidence, such as the cosmic microwave background radiation and the expansion of the universe, as measured by the redshift of distant galaxies.",
        "confidence": "high"
    }
]

Here is a broader sample of the conversation for context:
"""
<meta_chunk>
"""

Here is THE EXCERPT you are to extract beliefs from, which we refer to as THE EXCERPT. Please focus only on THE EXCERPT in your response, referencing the broader sample as needed for justification. If a belief is not expressed in THE EXCERPT, you should not include it in your response:
"""
<chunk>
"""

If no beliefs are explicitly expressed by <guest> in THE EXCERPT, please provide an empty list in your response.
'''

verification_evaluation = '''The following belief, extracted from a podcast transcription where <host> interviews <guest>, needs to be evaluated to determine whether it is worth verifying.

Please follow this decision tree to assess the belief:

1. Is the belief purely subjective, such as a personal preference or opinion?
   - If yes, verification is not required. Proceed to step 7.
   - If no, proceed to step 2.

2. Is the belief a well-established and widely accepted fact?
   - If yes, verification is not required. Proceed to step 7.
   - If no, proceed to step 3.

3. Does the belief have significant potential consequences or implications?
   - If yes, proceed to step 4.
   - If no, verification may not be necessary. Proceed to step 7.

4. Is the belief stated clearly and specifically enough to be verified?
   - If yes, proceed to step 5.
   - If no, verification is required to clarify the belief. Proceed to step 6.

5. Given the belief's type, assess the sufficiency of supporting evidence or reasoning:
   - For empirical beliefs: Is there sufficient observable, measurable evidence or scientific data supporting the belief?
   - For rational beliefs: Is the logical reasoning or inference based on the available evidence or premises sound?
   - For experiential beliefs: Are the personal experiences or anecdotes reliable and representative?
   - For axiological beliefs: Are the underlying values, principles, or norms widely accepted or justified?
   - For metaphysical beliefs: Is the belief consistent with established philosophical or scientific understanding of reality?
   - If the supporting evidence or reasoning is sufficient, verification may not be necessary. Proceed to step 7.
   - If the supporting evidence or reasoning is insufficient or questionable, proceed to step 6.

6. Verification is required. Identify the specific aspects of the belief that need further investigation or clarification based on its type and the available evidence or reasoning.

7. Please provide the following details for the belief:
   - Verify: (boolean) A boolean value (True or False) indicating whether the belief is worth verifying.
   - Verify Explanation: (string) A rationale for why the belief does or does not need to be verified based on the decision tree. Provide a brief explanation for each step that led to your conclusion.
   - Verification Focus: (string) If verification is required, specify the aspects of the belief that need further investigation or clarification.

**Example**:
{
    "belief": "The universe is deterministic, meaning that every event is caused by prior events and conditions, and there is no room for randomness or free will.",
    "type": "metaphysical",
    "verify": true,
    "verify_explanation": "The belief is not purely subjective or a widely accepted fact. It has significant implications for our understanding of causality, human agency, and moral responsibility. While the belief is stated clearly, there is ongoing philosophical and scientific debate about the nature of determinism and its compatibility with randomness and free will. Therefore, verification is required.",
    "verification_focus": "Examine philosophical arguments and scientific evidence related to determinism, randomness, and free will. Investigate the implications of determinism for human agency and moral responsibility."
}

Here is broader context from the conversation for reference:
"""
<meta_chunk>
"""

Here is THE EXCERPT you are to evaluate the belief from:
"""
<chunk>
"""

Here is the belief extracted from THE EXCERPT:
"""
<belief>
"""

Here is the type of the belief:
"""
<type>
"""

Please carefully follow the decision tree to determine whether the belief requires verification, and provide a detailed explanation for your conclusion.
'''

hypothesis_generation = '''The following belief, extracted from a podcast transcription where <host> interviews <guest>, has been identified as worth verifying. Your task is to generate hypotheses to evaluate the validity of this belief by considering various angles, evidence, and arguments.

**Instructions**:
1. Provide a list of hypotheses that could help determine the validity of the belief. Each hypothesis should specifically address different aspects of the verification focus.
2. Generate a diverse set of hypotheses, including those that challenge or contradict the stated belief, to ensure a comprehensive examination from different angles.
3. For each hypothesis, include:
   - **Hypothesis**: A clear, concise, and testable statement related to the verification focus.
   - **Explanation**: Why the hypothesis is relevant and how it helps to explore the belief, considering alternative explanations, unintended consequences, or potential limitations.
   - **Potential Sources**: Specific types of sources or documents that could be consulted to test the hypothesis.

**Guidance on Formulating Hypotheses**:
- Ensure each hypothesis is testable with available information.
- Make clear and specific predictions or statements that can be empirically tested.
- Consider current trends, data, and alternative perspectives for future-oriented beliefs.
- Generate hypotheses that support, challenge, or provide alternative explanations for the belief to uncover potential biases, assumptions, or gaps.

**Example**:
[
    {
        "hypothesis": "If no significant innovations in AI model efficiency occur, the power grid capacity will need to expand at an annual rate of at least 10% to meet the growing compute demands for AI training and inference.",
        "explanation": "This hypothesis examines the necessity of power grid expansion given the current trajectory of AI compute needs and the lack of efficiency improvements in AI models.",
        "potential_sources": [
            "Reports on current and projected power grid capacity (e.g., U.S. Energy Information Administration)",
            "Studies on AI compute demand trends and projections (e.g., OpenAI, MIT Technology Review)",
            "Data on recent advancements in AI model efficiency",
            "Industry analysis from leading AI research institutions and energy providers"
        ]
    },
    {
        "hypothesis": "The current rate of power grid capacity expansion is insufficient to keep pace with the projected growth in AI compute needs over the next decade.",
        "explanation": "This hypothesis assesses whether existing plans for power grid expansion are adequate to support the anticipated increase in AI compute requirements.",
        "potential_sources": [
            "Infrastructure expansion plans and reports from energy providers",
            "Projections of AI compute needs from industry reports",
            "Government and regulatory agency publications on energy infrastructure development",
            "Case studies of regions with significant AI industry growth"
        ]
    },
    {
        "hypothesis": "Significant investments in renewable energy sources are necessary to sustainably support the power requirements for large-scale AI training and inference.",
        "explanation": "This hypothesis explores the role of renewable energy in meeting the power demands of AI while addressing environmental sustainability concerns.",
        "potential_sources": [
            "Renewable energy capacity reports from organizations like the International Renewable Energy Agency (IRENA)",
            "Studies on the environmental impact of AI energy consumption",
            "Investment analyses on renewable energy projects related to AI infrastructure",
            "Data from governments and NGOs on renewable energy adoption rates"
        ]
    }
]

**Definitions**:
- **Belief**: The statement or idea extracted from the podcast that is to be verified.
- **Context**: The surrounding information and situation in which the belief was stated.
- **Justification**: The reasoning or evidence provided in the podcast supporting the belief.
- **Verification Focus**: The specific aspect or angle through which the belief should be evaluated for validation.

Please provide your response in the form of a compilable JSON object with the exact following structure:
[
    {
        "hypothesis": "<hypothesis>",
        "explanation": "<explanation>",
        "potential_sources": ["<source1>", "<source2>", "<source3>"]
    }
]

Here is additional context from the conversation (meta_chunk):
<meta_chunk>

Here is the specific excerpt (chunk) from which the belief was extracted:
<chunk>

Here is the context and details of the belief:
- **Belief**: <belief>
- **Context**: <context>
- **Justification**: <justification>
- **Verification Focus**: <verification_focus>
'''

data_collection_process = '''The following hypothesis, extracted from a podcast transcription where <host> interviews <guest>, has been identified as worth verifying. Your task is to create a detailed data collection process to evaluate the validity of this hypothesis using publicly available data sources.

Here is additional context from the conversation (meta_chunk):
<meta_chunk>

Here is the specific excerpt (chunk) from which the hypothesis was derived:
<chunk>

Here is the context and details of the hypothesis:
- **Hypothesis**: <hypothesis>
- **Context**: <context>
- **Provided Justification**: <justification>
- **Verification Focus**: <verification_focus>

**Instructions**:
1. Outline a step-by-step data collection process that specifically addresses the hypothesis and verification focus.
2. For each step, include:
   - **Step Description**: A clear and concise description of the data collection step.
   - **Data Type**: The type of data needed (e.g., qualitative, quantitative, historical data, current data).
   - **Potential Sources**: Specific publicly available sources or documents where the data can be obtained.
   - **Data Collection Method**: The method for collecting the data (e.g., downloading reports, accessing databases, conducting web searches).
   - **Verification Method**: How to verify the accuracy and reliability of the collected data.

**Example**:
[
    {
        "step_description": "Identify current and projected power grid capacity to determine if it meets the growing AI compute demands.",
        "data_type": "Quantitative",
        "potential_sources": [
            "U.S. Energy Information Administration (EIA) Annual Energy Outlook (https://www.eia.gov/outlooks/aeo/)",
            "National Grid capacity forecasts available on the National Grid website (https://www.nationalgrid.com/)",
            "International Energy Agency (IEA) publications and datasets (https://www.iea.org/reports)"
        ],
        "data_collection_method": "1. Visit the U.S. Energy Information Administration (EIA) website and download the latest Annual Energy Outlook report. 2. Access the National Grid website and download their capacity forecast reports. 3. Obtain relevant publications and datasets from the International Energy Agency (IEA) website.",
        "verification_method": "Cross-reference data from EIA, National Grid, and IEA to ensure consistency. Validate the data against independent industry analyses published in journals such as Energy Policy."
    },
    {
        "step_description": "Analyze trends in AI model efficiency improvements over the past decade.",
        "data_type": "Quantitative",
        "potential_sources": [
            "IEEE Xplore Digital Library (https://ieeexplore.ieee.org/)",
            "arXiv.org (https://arxiv.org/)",
            "OpenAI publications (https://www.openai.com/research/)"
        ],
        "data_collection_method": "1. Search for studies on AI model efficiency in the IEEE Xplore Digital Library using relevant keywords. 2. Access technical whitepapers from arXiv.org. 3. Visit the OpenAI website and download their latest publications on AI model efficiency.",
        "verification_method": "Verify data by checking citations and replication studies. Consult experts in the field through academic networks or professional organizations to confirm findings."
    },
    {
        "step_description": "Evaluate the rate of power grid capacity expansion in regions with high AI activity.",
        "data_type": "Quantitative",
        "potential_sources": [
            "Regional energy provider websites (e.g., Pacific Gas and Electric Company, https://www.pge.com/)",
            "Government portals for infrastructure development reports (e.g., U.S. Department of Energy, https://www.energy.gov/)",
            "Google Scholar for case studies on regions with significant AI industry growth (https://scholar.google.com/)"
        ],
        "data_collection_method": "1. Visit regional energy provider websites and download their latest expansion plans. 2. Access infrastructure development reports through government portals like the U.S. Department of Energy. 3. Search for relevant case studies on Google Scholar.",
        "verification_method": "Cross-verify data from regional energy providers with government reports and independent case studies. Ensure data consistency by comparing with national trends published in journals such as Renewable and Sustainable Energy Reviews."
    },
    {
        "step_description": "Assess the impact of renewable energy investments on supporting AI power requirements.",
        "data_type": "Quantitative and Qualitative",
        "potential_sources": [
            "International Renewable Energy Agency (IRENA) reports (https://www.irena.org/Publications)",
            "Renewable Energy journal articles (https://www.journals.elsevier.com/renewable-energy)",
            "Investment analyses from public financial institutions like the World Bank (https://www.worldbank.org/en/research)"
        ],
        "data_collection_method": "1. Download relevant reports from the International Renewable Energy Agency (IRENA) website. 2. Search for articles in the Renewable Energy journal using ScienceDirect. 3. Access investment analyses from the World Bank research portal.",
        "verification_method": "Cross-verify data from IRENA reports with studies published in academic journals and investment analyses from public financial institutions. Consult industry experts to validate findings and ensure accuracy."
    }
]

**Definitions**:
- **Hypothesis**: The statement or idea extracted from the podcast that is to be verified.
- **Context**: The surrounding information and situation in which the hypothesis was stated.
- **Justification**: The reasoning or evidence provided in the podcast supporting the hypothesis.
- **Verification Focus**: The specific aspect or angle through which the hypothesis should be evaluated for validation.

Please provide your response in the form of a compilable JSON object with the exact following structure:
[
    {
        "step_description": "<step_description>",
        "data_type": "<data_type>",
        "potential_sources": ["<source1>", "<source2>", "<source3>"],
        "data_collection_method": "<method>",
        "verification_method": "<verification>"
    }
]
'''