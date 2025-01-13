import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing multiagent setup...")



# Загрузка переменных окружения
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API key is missing. Check your .env file.")

# Настройка модели ChatOpenAI
llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)

# Определение инструментов
class SearchCompanionsTool(BaseTool):
    name: str = "search_companions"
    description: str = "Analyzes profiles to suggest potential collaborators."

    def _run(self, input_str: str):
        return f"Suggested collaborators for: {input_str}"

class TeamFormationTool(BaseTool):
    name: str = "team_formation"
    description: str = "Forms optimal teams for projects."

    def _run(self, input_str: str):
        # Пример обработки строки
        try:
            if ": " in input_str:
                inputs = dict(item.split(": ") for item in input_str.split(", "))
                project_goal = inputs.get("project_goal")
                participants = inputs.get("participants")
                return f"Team formed for goal: {project_goal} with participants: {participants}"
            else:
                return f"Could not process input: {input_str}"
        except Exception as e:
            return f"Error parsing input: {str(e)}"

class IdeaGenerationTool(BaseTool):
    name: str = "idea_generation"
    description: str = "Generates project ideas based on user profiles."

    def _run(self, input_str: str):
        try:
            if ": " in input_str:
                inputs = dict(item.split(": ") for item in input_str.split(", "))
                user_interests = inputs.get("user_interests")
                return f"Generated ideas for interests: {user_interests}"
            else:
                return f"Could not process input: {input_str}"
        except Exception as e:
            return f"Error parsing input: {str(e)}"

# Настройка инструментов
tools = [
    SearchCompanionsTool(),
    TeamFormationTool(),
    IdeaGenerationTool()
]

# Создание агента
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

# Настройка супервизора
supervisor = agent

if __name__ == "__main__":
    # Код для тестирования или запуска изолированно
    response = supervisor.run("search_companions for interests: design, skills: Python")
    print(response)


