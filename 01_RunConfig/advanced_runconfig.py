import os 
from dotenv import load_dotenv
from agents import Agent, ModelSettings , Runner , OpenAIChatCompletionsModel  , AsyncOpenAI , set_tracing_disabled 
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
    model_settings=ModelSettings(temperature=0.2 , max_tokens=100),
    tracing_disabled=False,
    trace_include_sensitive_data=False,
    workflow_name='Basic Consultant Agent'

)

# agent
agent = Agent(
    name='Assistant',
    instructions='You are a helpful assistant',
)


# run with error handling
try:
    result= Runner.run_sync(
        agent ,
        'universites in italy ?',
        run_config=config
    )
    print(result.final_output)
except Exception as e:
    print('error during run ' , {e})
