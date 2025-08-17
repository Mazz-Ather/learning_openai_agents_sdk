import os
from dotenv import load_dotenv
from agents import Agent, RunContextWrapper, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled
from agents.run import RunConfig

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
set_tracing_disabled(True)

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY,
                             base_url='https://generativelanguage.googleapis.com/v1beta/openai/')

model = OpenAIChatCompletionsModel(model='gemini-2.0-flash', openai_client=external_client)

config = RunConfig(model=model, model_provider=external_client, tracing_disabled=True)

def dynamic_instruction(ctx: RunContextWrapper, agent) -> str:
    # ctx.context is whatever you passed into Runner.run(..., context=...)
    # If it's a dict you can do ctx.context["name"]. If it's a dataclass, access attributes.
    name = ctx.context.get("name") if isinstance(ctx.context, dict) else getattr(ctx.context, "name", "guest")
    return f"Make sure to greet first with username {name}. You are a helpful assistant."

agent = Agent(name='Assistant', instructions=dynamic_instruction)


result = Runner.run_sync(agent, 'Capital of Italy ?', run_config=config, context={"name": "mazz"})
print(result.final_output)
