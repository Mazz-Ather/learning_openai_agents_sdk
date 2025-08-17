import os 
from dotenv import load_dotenv
from agents import Agent , Runner , OpenAIChatCompletionsModel  , AsyncOpenAI , set_tracing_disabled , function_tool
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

# function tool
@function_tool
def fetch_universites(universities:str )-> str :
    '''
    use this tool to get universites name instead of guessing
    '''
    best_unis = [
    "Sapienza University of Rome",
    "University of Milan",
    "University of Padua",
    "Polytechnic University of Milan",
    "University of Bologna",
    "University of Pisa",
    "University of Turin",
    "University of Florence"
]

    return f'Top univeristes in italy are {best_unis}'



# function tool for department


# agent
agent = Agent(
    name='Consultant',
    instructions='You are a helpful Consultant to give best universiites names , always call tool when user ask about italin university',
    tools=[fetch_universites],
   
)



#runner 
result  = Runner.run_sync(agent , 'Best 3 Universites in Italy ?',run_config=config , )
print(result.final_output)