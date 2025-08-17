import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool
from agents.run import RunConfig
from typing import List
from pydantic import BaseModel, Field, conint, field_validator
from agents.tool_context import ToolContext


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

# Schemas
class UniversitiesQueries(BaseModel):
    country: str = Field(default="Italy", description="Country to search",alias='ctry')
    top_n: conint(ge=1, le=20) = Field(default=3, description="Number of results to return")
    admission_open : bool = Field(default=True , description='Filter for Open admission')

    @field_validator('country')
    @classmethod
    def validate_country(cls , v:str)->str:
        if v.lower not in ['Italy']:
            raise ValueError('Only Italy Supported')
        return v.title
    
class UniversitiesResponse(BaseModel):
    results: List[str]
    total: int
    admission_open:bool 
    source:str = Field(default='Mock DB' , description='Data Source')

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
# ================ custom error function ============================
def custom_error(ctx:ToolContext,error:Exception)->str:
    return f'Tool Error in {ctx.tool_name} because of {str(error)} .'
# ============================= @function_tool=========================
@function_tool(
    description_override='Fetches top universities in italy !',
    failure_error_function=custom_error,
    strict_mode=True,
    is_enabled=lambda ctx, agent: 'italy' in agent.instructions.lower()
)
async def fetch_universities(
    ctx:ToolContext , query:UniversitiesQueries
)->UniversitiesResponse:
    if isinstance(ctx.context , dict) and 'cache' in ctx.context:
        return ctx.context['cache']

    if query.country.lower() == 'italy':
        results = best_unis[:query.top_n]
        if not query.admission_open:
            results = results[::2]
        return UniversitiesResponse(
            results=results,
            total=len(best_unis)
        )
    else:
        raise ValueError('Unsupported Country')



# Agent
agent = Agent(
    name="Consultant",
    instructions="Always use fetch_universites tool to answer questions about universities in Italy.",
    tools=[fetch_universities],
    output_type=UniversitiesResponse
)

# Run
result = Runner.run_sync(agent, "list universities in Italy?", run_config=config)
print(result.final_output)
