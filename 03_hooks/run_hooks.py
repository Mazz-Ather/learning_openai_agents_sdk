import asyncio
import os 
from agents import Agent, AgentHooks, RunHooks , Runner ,OpenAIChatCompletionsModel, AsyncOpenAI , set_tracing_disabled, function_tool , Tool
from agents.run import RunConfig
from dotenv import load_dotenv
from dataclasses import dataclass 
from typing  import List , Any  , Dict , Optional 
from pydantic import BaseModel
from agents.run_context import RunContextWrapper , TContext
# from agents.tool import tool 

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env file")

# set_tracing_disabled(True)

# LLM service
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)

# Run config
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
    
)
# ========================= Run Hooks ==================================

class MyHooks(RunHooks):
    async def on_agent_start(self, context:RunContextWrapper[TContext], agent:Agent[TContext]):
        print('on_agent_start hoook is called ')
        return await super().on_agent_start(context, agent)
    async def on_agent_end(self, context, agent, output):
        print('on_agent_end hoook is called ')
        print(output)
        return await super().on_agent_end(context, agent, output)
    



# =================================== AGENT ===========================
async def main():
    agent = Agent(
        name='Consultant',
        instructions='''
        your goal is to help students to know which university is best for them .
        make answer short an to the point . 
        '''
    )

    result =await Runner.run(
        agent,
        'best university for undergraduate in italy in cs department ? ',
        run_config=config,
        hooks=MyHooks()

    )

if __name__ == '__main__':
    asyncio.run(main())