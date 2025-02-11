from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from common.typings import CourseOutline

@CrewBase
class OutlineCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, inputs) -> None:
        self.llm = LLM(
            model=inputs["model"],
            temperature=inputs["temperature"],
        )
        self.search_tool = SerperDevTool() if inputs['include_web_search'] else None

    @agent
    def outline_creator(self) -> Agent:
        tools = [self.search_tool] if self.search_tool else []
        # print("********** TOOLS ***********\n", tools, "\n***************************\n")
        return Agent(
            llm=self.llm,
            verbose=True,
            tools=tools,
            config=self.agents_config['outline_creator'],
        )

    @task
    def outline_task(self) -> Task:
        return Task(
            config=self.tasks_config['outline_task'],
            output_pydantic=CourseOutline,
            output_file='course_latest/3_outline.json'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
