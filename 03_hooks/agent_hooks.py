import asyncio
import os 
from agents import Agent, AgentHooks , Runner ,OpenAIChatCompletionsModel, AsyncOpenAI , set_tracing_disabled, function_tool , Tool
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


# ================ user context ===============
@dataclass
class UserContext:
    uid:str
    interest:str
    ielts_required : bool
    activity:List[str]
    budget:int
# ==========================================================
                    # Agent HOOKS
# ==========================================================

class MyHooks(AgentHooks):
    async def on_start(
            self , context : RunContextWrapper[TContext] , agent : Agent[TContext]
    ) ->None :
        print(f'[hook] agent {agent.name}  , for user {context}')

    async def on_end(
            self , context: RunContextWrapper[TContext] , agent : Agent[TContext] , output : Any
    )->None:
        print(f'agent finished final output {output}')

    async def on_tool_start(self, context : RunContextWrapper[TContext], agent:Agent[TContext], tool:Tool):
        print(f'using tool : {tool.name}')

    async def on_tool_end(self, context:RunContextWrapper[TContext], agent:Agent[TContext], tool:Tool, result:str):
        print(f'Tool end {tool.name} and the result is {result}')


# ==============================tool call===========================
@function_tool 
async def find_best_courses(context:RunContextWrapper[UserContext])->str:
    """
    tell the best courses/degrees to do in specific country to get the best out of it
    """
    print('tool find_best_courses called')
    return  context.context.interest

@function_tool
async def fetch_university_extracurricular_activites(context:RunContextWrapper[UserContext] , country:str)->List[str]:
    """
    list extracurricular activites that universities offer according to the country
    e.g: if Italy then list Modeling , Football , 
    if Austrailia then list Cricket , Camping etc 
    """
    print('tool fetch_university_extracurricular_activites called')
    return context.context.activity
# ======================== Multiple Agents for handoffs =============================== 
course_finder_agent=Agent[UserContext](
    name='course_finder_agent',
    instructions='your goal is to find best course',
    tools=[find_best_courses],
    hooks=MyHooks()
)

activites_finder_agent=Agent[UserContext](
    name='activites_finder_agent',
    instructions='your goal is to find best extra curricular activites',
    tools=[fetch_university_extracurricular_activites],
    hooks=MyHooks()
)

# ======================== MAIN TRAIGE AGENT==========================
triage_agent=Agent[UserContext](
    name='Triage Agent',
    instructions='you are a traige agent thaat routes queries to appropriate sub-agent on the user context , is the user ask about course handoff to course_finder_agent and if the user ask about extra curricular activites handoffs to activites_finder_agent',
    handoff_description='Route queries related to user context',
    handoffs=[activites_finder_agent , course_finder_agent],

    hooks=MyHooks()
)

# ======================RUUN AGENT--------------------------
async def run_agent():
    user_context=UserContext(
        uid='476344',
        interest='computer science',
        ielts_required=True,
        activity=['football','Martial Arts', 'Swimming'],
        budget=200000
    )
    result =  await Runner.run(
        triage_agent, 
        input='best courses in italy ?',
        run_config=config,
        context=user_context
    )
    # print(f'final output is : {result.final_output}')

asyncio.run(run_agent())