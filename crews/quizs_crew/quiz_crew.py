from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from common.typings import QuizContent


@CrewBase
class QuizCrew():
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
    def quiz_creator(self) -> Agent:
        tools = [self.search_tool] if self.search_tool else []
        return Agent(
            llm=self.llm,
            verbose=True,
            tools=tools,
            # max_retry_limit=5,
            max_rpm=5,
            max_iter=10,
            config=self.agents_config['quiz_creator'],
        )

    @task
    def quiz_task(self) -> Task:
        txt_file = f"course_latest/6_{self.i}_quiz.json"
        return Task(
            config=self.tasks_config['quiz_task'],
            output_json=QuizContent,
            output_file=txt_file,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            max_rpm=10,
            verbose=True,
        )
