import os 
from dotenv import load_dotenv
from agents import Agent , Runner , OpenAIChatCompletionsModel  , AsyncOpenAI , set_tracing_disabled 
from agents.run import RunConfig


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Set tracing disabled
set_tracing_disabled(True)

#llm service 
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

#model 
model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash',
    openai_client=external_client,
)

# runconfig
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)

# translater agents
italian_translator = Agent(
    name='Italian Translator',
    instructions='You are a helpful translator. You translate text to Italian.',
)
spanish_translator = Agent(
    name='Spanish Translator',
    instructions='You are a helpful translator. You translate text to Spanish.',
)

# agent
agent = Agent(
    name='Triage Agent',
    instructions= "You are a translation agent. You handoff to the specific agent to translate.",
    handoffs=[italian_translator,spanish_translator],
    handoff_description= 'If asked for multiple translations, you call the relevant agents.'        
   
)

#runner 
result  = Runner.run_sync(agent , 'how to say this in italian , i love italy so much ',run_config=config , )
print(result.final_output)