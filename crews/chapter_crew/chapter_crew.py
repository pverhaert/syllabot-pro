from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from common.typings import OneChapter




@CrewBase
class ChapterCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, inputs) -> None:
        self.llm = LLM(
            model=inputs["model"],
            temperature=inputs["temperature"],
        )
        self.i = inputs['i']
        self.search_tool = SerperDevTool() if inputs['include_web_search'] else None

    @agent
    def content_creator(self) -> Agent:
        tools = [self.search_tool] if self.search_tool else []
        return Agent(
            llm=self.llm,
            verbose=True,
            tools=tools,
            config=self.agents_config['content_creator'],
        )

    @task
    def content_task(self, ) -> Task:
        # txt_file = f"course_latest/4_{self.i}_course_content.txt"
        return Task(
            config=self.tasks_config['content_task'],
            # output_pydantic=OneChapter,
            # output_file= txt_file
        )

    @agent
    def markdown_fixer(self) -> Agent:
        tools = [self.search_tool] if self.search_tool else []
        return Agent(
            llm=self.llm,
            verbose=True,
            tools=tools,
            config=self.agents_config['markdown_fixer'],
        )

    @task
    def markdown_fixer_task(self, ) -> Task:
        txt_file = f"course_latest/4_{self.i}_course_content.txt"
        return Task(
            config=self.tasks_config['markdown_fixer_task'],
            output_pydantic=OneChapter,
            output_file=txt_file
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
