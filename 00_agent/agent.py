import asyncio
import os 
from dotenv import load_dotenv
from agents import Agent , Runner , OpenAIChatCompletionsModel  , AsyncOpenAI , set_tracing_disabled ,RunConfig

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

# agent
agent = Agent(
    name='Assistant',
    instructions='You are a helpful assistant',
    
    model=model,
)




#runner 
result  = Runner.run_sync(agent , 'capital of france ?',run_config=config)
print(result.final_output)
