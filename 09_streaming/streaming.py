import asyncio
import os 
from dotenv import load_dotenv
from agents import Agent, ItemHelpers , Runner , OpenAIChatCompletionsModel  , AsyncOpenAI , set_tracing_disabled , function_tool
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
    "University of Florence",
    "University of Naples Federico II",
    "Polytechnic University of Turin",
    "University of Trento",
    "University of Verona",
    "University of Parma",
    "University of Salerno",
    "University of Trieste",
    "University of Palermo",
    "University of Calabria",
    "University of Modena and Reggio Emilia",
    "University of Catania",
    "Università degli Studi di Roma Tor Vergata",
    "Università Cattolica del Sacro Cuore",
    "Bocconi University",
    "Vita-Salute San Raffaele University",
    "Humanitas University",
    "Ca' Foscari University of Venice",
    "University of Genoa",
    "University of Pavia",
    "LUISS Guido Carli"
]

    return f'Top univeristes in italy are {best_unis}'



# function tool for department

async def main():
    # agent
    agent = Agent(
        name='Consultant',
        instructions='You are a helpful Consultant to give best universiites names , always call tool when user ask about italin university',
        tools=[fetch_universites],
    
    )
        #runner 
    result  = Runner.run_streamed(agent , 'List all the universities in italy ?',run_config=config , )
    async for event in result.stream_events():
        if hasattr(event, "item"):  # only events with .item
            if event.item.type == "tool_call_output_item":
                print(event.item.output)
            elif event.item.type == "message_output_item":
                print(ItemHelpers.text_message_output(event.item))
        else:
            # Optional: debug what kind of event it is
            print(f"Other event: {event}")

asyncio.run(main())