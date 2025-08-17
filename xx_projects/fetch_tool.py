import os 
import requests 
from dotenv import load_dotenv
from agents import Agent, ModelSettings , Runner , OpenAIChatCompletionsModel  , AsyncOpenAI , set_tracing_disabled , function_tool
from agents.run import RunConfig
from agents.agent import StopAtTools

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
@function_tool
def fetch_user_data()->list[str]:
    '''Fetch data from api and return list'''
    url = 'https://jsonplaceholder.typicode.com/users'
    res = requests.get(url)
    return res.json()


# agent
agent = Agent(
    name='Assistant',
    instructions='helpful assistant that always tool called',
    tools=[fetch_user_data],
    model_settings=ModelSettings(tool_choice='required')

)



#runner 
result  = Runner.run_sync(agent , 'give me all the emails',run_config=config , )
print(result.final_output)