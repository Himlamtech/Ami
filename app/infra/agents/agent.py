from google.adk.agents import Agent
from prompt import root_agent_instruction
#from ...core.config import settings
from google.genai import types
from google.adk.planners import BuiltInPlanner
from dotenv import load_dotenv

load_dotenv()
root_agent = Agent(
    name = "root_agent",
    model = "gemini-2.5-flash",
    description= "Tác nhân gốc, có chức năng phân tích và định tuyến yêu cầu đến tác nhân phù hợp.",
    instruction= root_agent_instruction,
    planner= BuiltInPlanner(
        thinking_config= types.ThinkingConfig(
            include_thoughts= True,
            thinking_budget= 1024
        )
    ),
    sub_agents= []
)
print("Root agent created successfully.")