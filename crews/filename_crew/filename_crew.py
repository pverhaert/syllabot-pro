from rich.console import Console
console = Console()
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from common.typings import Titles


@CrewBase
class FilenameCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, inputs: dict) -> None:
        self.llm = LLM(
            model=inputs['model'],
            temperature=0.7,
        )

    @agent
    def filename_creator(self) -> Agent:
        return Agent(
            llm=self.llm,
            verbose=True,
            tools=[],
            config=self.agents_config['filename_creator'],
        )

    @task
    def filename_task(self) -> Task:
        return Task(
            config=self.tasks_config['filename_task'],
            output_file="course_latest/1_title.json",
            output_pydantic=Titles
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
