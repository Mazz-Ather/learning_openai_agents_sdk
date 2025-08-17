import asyncio
from dataclasses import dataclass
import os 
from dotenv import load_dotenv
from agents import Agent, RunContextWrapper , Runner , OpenAIChatCompletionsModel  , AsyncOpenAI , set_tracing_disabled , function_tool
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

@dataclass
class UserContext:
    uid:str
    is_pro_user:bool

@function_tool
async def suggest_uni(wrapper:RunContextWrapper[UserContext])->str:
    """
    Give Suggested Universities if a user is pro_user or not ,
    Call this function to tell the user the bet university to study
    """
    
    if wrapper.context.is_pro_user:
        return f'the best universitiy for user id {wrapper.context.uid} is Standford U.S'
    else:
        return f'The best University for {wrapper.context.uid} is Iqra University in karachi , Pakistan'

async def main():
    user_context = UserContext(uid='476344' , is_pro_user=True)

    agent = Agent[UserContext](
        name='Consultant',
        instructions= "You are a helpful Consultant that gives the best university names. "
            "You always call the `suggest_uni` tool when asked about universities. "
            "You already know the user's pro status from `context.is_pro_user` — do not ask again."
    ,
        tools=[suggest_uni]
    )
    result  =await Runner.run(starting_agent=agent , input='Best  University for me ?',run_config=config,context=user_context  )

    print(result.final_output)

if __name__ == '__main__':
    asyncio.run(main())