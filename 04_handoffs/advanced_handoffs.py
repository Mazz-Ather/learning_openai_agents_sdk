import os 
from dotenv import load_dotenv
from agents import Agent, RunContextWrapper , Runner , OpenAIChatCompletionsModel  , AsyncOpenAI, function_tool ,handoff, set_tracing_disabled 
from agents.run import RunConfig
from pydantic import BaseModel
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters

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
# tool
@function_tool()
async def country_to_study(ctx: RunContextWrapper[None], country: str) -> str:
    """
    Returns the country to study based on the input country.
    """
    print('tool called')
    if country.lower() == 'italy':
        return 'Italy is known for its rich history, art, and culture. It is a great country to study.'
    elif country.lower() == 'spain':
        return 'Spain is famous for its diverse culture, language, and history. It is a great country to study.'
    else:
        return f'{country} is not well recognized country for study.'

# translater agents
italian_translator = Agent(
    name='Italian Translator',
    instructions=f'''
You are a helpful translator. You translate text to Italian.
{RECOMMENDED_PROMPT_PREFIX}
''',
    handoff_description='you are a translator for Italian language. You translate text to Italian.'
)

spanish_translator = Agent(
    name='Spanish Translator',
    instructions=f'''
You are a helpful translator. You translate text to Spanish.
{RECOMMENDED_PROMPT_PREFIX}
''',
    handoff_description='you are a translator for Spanish language. You translate text to Spanish.'
)

# ==========customizating handoffs ==========
class CustomHandoffData(BaseModel):
    reason: str

async def on_handoff(ctx:RunContextWrapper[None],input_data:CustomHandoffData):
    print("Handoff called ")
    print(f"Reason for handoff: {input_data.reason}")

italian_language_handoff = handoff(
    agent=italian_translator,
    tool_name_override='translate_to_italian',
    tool_description_override='Translate the user text to Italian',
    on_handoff=on_handoff,
    input_type=CustomHandoffData,
    # input_filter=handoff_filters.remove_all_tools
    is_enabled=False

)

spanish_language_handoff = handoff(
    agent=spanish_translator,
    tool_name_override='translate_to_spanish',
    tool_description_override='Translate the user text to Spanish',
)
# agent
agent = Agent(
    name='Triage Agent',
    instructions= "You are a translation agent. You handoff to the specific agent to translate and for other query.",
    handoffs=[italian_language_handoff,spanish_translator],
    tools=[country_to_study],      
   
)

#runner 
result  = Runner.run_sync(agent ," translate this into italian 'i love italy ' , and tell me please is italy the best country to study",run_config=config ,context={
    'name':'mazz ather'
} )
print(result.final_output)
print(result.last_agent.name)