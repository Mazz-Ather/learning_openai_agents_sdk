import asyncio
from json import tool
import os
import json

from dotenv import load_dotenv
from agents import Agent, FunctionTool, RunContextWrapper, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, default_tool_error_function, set_tracing_disabled, function_tool
from agents.run import RunConfig
from typing import List , Any , Union
from pydantic import BaseModel, Field, conint, field_validator , ConfigDict
from agents.tool_context import ToolContext 
from typing_extensions import TypedDict

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
    trace_metadata={'app_version' : 'advanced_1.0'} #metadata
)

 # shared context type for tools 
class AppContext(BaseModel):
    cache:dict[str,Any] = Field(default_factory=dict)
    user_role :str = 'guest'

# pydantic
class QueryBase(BaseModel):
    model_config = ConfigDict(alias_generator=lambda f: f.upper())

class UniQuery(QueryBase):
    country:str = Field(default='italy',description='country')
    top_n:conint(ge=1 , le=20) = 3
    
    @field_validator('country',mode='before')
    @classmethod
    def validate_country(cls, v:Any)->str:
        if not isinstance(v , str):
            raise TypeError('country must be string')
        return v.title()

class DetailedQuery(QueryBase):
    uni_name:str
    details:Union[str | List[str]] = Field(default='all' ,description="Details like 'ranking' or ['history', 'admissions']" )

DetailedTypeDict = TypedDict('DetailTypedDict', {'ranking': int, 'history': str})  # For typed dict args

#pydantic for output type
class UniResponse(BaseModel):
    result:List[str]
    total:int

class DetailedResponse(BaseModel):
    uni:str
    info : dict[str,Any]

class CombinesResponse(BaseModel):
    unis:UniResponse
    details:Union[DetailedResponse, str]

best_unis = {  # Mock DB
    "Italy": ["Sapienza University of Rome", "University of Milan", "University of Padua"]
}

mock_details = {
    "Sapienza University of Rome": {"ranking": 1, "history": "Founded in 1303"}
}

#  tool 1
@function_tool(description_override='check if uni data is availaible')
def check_availaibilty(ctx:ToolContext[AppContext])->str:
    if ctx.context.user_role != 'admin':
        raise PermissionError('admin allowed only')
    return 'Data Availlaible' if best_unis else 'No Data'

# custom error function
async def custom_async_error(ctx:RunContextWrapper[AppContext], error:Exception)->str:
    await asyncio.sleep(0.1)
    return {'error':str(error), "tool":ctx.context.tool_name, "retry":True}

# tool 2 
@function_tool(
    name_override='fetch_top_universities',
    failure_error_function=custom_async_error,
    strict_mode=False
)
async def fetch_uni_async(ctx:ToolContext[AppContext], query:UniQuery)->UniResponse:
    country = query.country
    if country in best_unis:
        results = best_unis[country][:query.top_n]
        ctx.context.cache['last_unis'] = results
        return UniResponse(results=results,total=len(best_unis[country]))
    raise ValueError('country {country} not found ')

# Tool 3: Manual creation, TypedDict args, conditional callable, argless fallback
def get_uni_details_func(details:DetailedTypeDict)->DetailedResponse:
    return DetailedResponse(uni='Mock' , info=details)

async def details_on_invoke(ctz:ToolContext[AppContext], args:str)->Union[DetailedResponse,str]:
    if not args:
        return 'No details provided'
    parsed = json.loads(args)
    uni =parsed.get('uni_name')
    if uni in mock_details:
        return DetailedResponse(uni=uni,info=mock_details[uni])
    return 'details not found '

async def is_details_enabled(ctx: RunContextWrapper[AppContext], agent: Agent) -> bool:
    return ctx.context.user_role == "admin" and "details" in agent.instructions.lower()

details_tool = FunctionTool(
    name='get_uni_details',
    description="Fetches details for a university using TypedDict.",
    params_json_schema={
        'type':'output',
        'properties':{
            'uni_name':{'type':'string'},
            'details':{'type':'object','additional_properties':True}
        },
        'required':['uni_name']
    },
    on_invoke_tool=details_on_invoke,
    is_enabled=is_details_enabled,
    strict_json_schema=False
)

# Agent
agent = Agent(
    name="Consultant",
    instructions="Always use fetch_universites tool to answer questions about universities in Italy.",
    tools=[check_availaibilty,fetch_uni_async,details_tool],
    output_type=CombinesResponse
)

# Run
custom_ctx =AppContext(user_role='admin')
result = Runner.run_sync(agent, "List top universities in Italy and details for Sapienza?", run_config=config,context=custom_ctx)
print(result.final_output.model_dump_json(indent=2))