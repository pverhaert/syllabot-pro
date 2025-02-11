import os
import time
from datetime import datetime
from typing import Optional, List

from dotenv import load_dotenv
from pydeck.bindings.map_styles import styles

from common.prepare_files import PrepareFiles
from crews.chapter_crew.chapter_crew import ChapterCrew
from crews.exercises_crew.exercises_crew import ExercisesCrew
from crews.quizs_crew.quiz_crew import QuizCrew

load_dotenv()
from rich.console import Console

console = Console()
import agentops

if agentops_key := os.getenv("AGENTOPS_API_KEY"):
    agentops.init(api_key=agentops_key)
    # agentops.init(api_key=agentops_key, skip_auto_end_session=True)
# crew_session = agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

from common.markdown_writer import MarkdownWriter
from crews.filename_crew.filename_crew import FilenameCrew
from crews.outline_crew.outline_crew import OutlineCrew
from common.typings import Titles, CourseOutline, OneChapter, ExercisesContent, QuizContent


# INFO: https://github.com/tylerprogramming/master-crewai-course/blob/main/requirements.txt

class Metrics(BaseModel):
    total_tokens: int = 0
    prompt_tokens: int = 0
    cached_prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: datetime = Field(default_factory=datetime.now)


class CourseInputs(BaseModel):
    language: str = "English"
    course: str = "JavaScript functions"
    chapters_that_must_be_included: str = ""
    special_needs: str = ""
    target_audience: str = ""
    writing_style: str = ""
    model: str = "groq/llama-3.3-70b-versatile"
    timeout: int = 45
    word_length: int = 1000
    include_web_search: bool = False
    num_chapters: int = 5
    num_exercises: int = 5
    num_quizzes: int = 5
    temperature: float = 0.5
    test_mode: bool = False
    serper_api_key: str = "xxx"
    metrics: Metrics = Field(default_factory=Metrics)


class CourseState(BaseModel):
    inputs: CourseInputs = CourseInputs()  # input fields from Streamlit
    titles: Titles = ""  # Filename.name = title for the final file (yyyymmdd_hhmmss_file_name.md)
    course_outline: List[CourseOutline] = []  #
    chapters: List[OneChapter] = []
    exercises: List[ExercisesContent] = []
    quizzes: List[QuizContent] = []
    # courseOutline: CourseOutline


class CourseFlow(Flow[CourseState]):
    def __init__(self, inputs: dict = None):
        super().__init__()
        if inputs:
            try:
                self.state.inputs = CourseInputs(**inputs)
            except Exception as e:
                print("***Error parsing inputs***:", e)

    def update_metrics(self, token_usage):
        self.state.inputs.metrics.total_tokens += token_usage.total_tokens
        self.state.inputs.metrics.prompt_tokens += token_usage.prompt_tokens
        self.state.inputs.metrics.cached_prompt_tokens += token_usage.cached_prompt_tokens
        self.state.inputs.metrics.completion_tokens += token_usage.completion_tokens
        self.state.inputs.metrics.successful_requests += token_usage.successful_requests
        self.state.inputs.metrics.end_time = datetime.now()

    @start()
    def generate_filename_and_titles(self):
        """
        Generates a filename for the final document based on input parameters.
        Translate the titles "Course Content" and "Exercises" to the specified language.
        Returns: None, sets the filename in self.state.filename.
        """
        console.print("\nGenerate filename for final document and translate titles\n", style="yellow")
        config = {
            "model": "groq/llama-3.3-70b-versatile"
        }
        crew = FilenameCrew(inputs=config)
        inputs = {
            attr: getattr(self.state.inputs, attr)
            for attr in ['course', 'language']
        }
        result = crew.crew().kickoff(inputs=inputs)
        # console.print("\n*-*-* RESULT FILENAMES *-*-*-*-\n", result, "\n*-*-*-*-\n")
        console.print("\n*-*-* RESULT FILENAMES PYDANTIC *-*-*-*-\n", result.pydantic, "\n*-*-*-*-\n")
        self.state.titles = result.pydantic
        self.update_metrics(result.token_usage)
        # prepend timestamp to the filename and add .md extension
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state.titles.file_name = f"{timestamp}_{self.state.titles.file_name}.md"

    @listen(generate_filename_and_titles)
    def prepare_files(self):
        """
        Prepares the files for the course in the "course_latest" directory.
        Returns: None
        """
        console.print("\nPrepare files\n", style="black on yellow")
        prepare_files = PrepareFiles(self.state.titles, self.state.inputs)
        prepare_files.make_files()

    @listen(prepare_files)
    def create_course_outline(self):
        """
        Generates an outline for the course based on input parameters.
        Returns: None, sets the outline in self.state.outline.
        """
        console.print("Kickoff the Course Outline Crew", style="black on yellow")
        config = {
            "model": self.state.inputs.model,
            "temperature": self.state.inputs.temperature,
            "include_web_search": self.state.inputs.include_web_search,
        }
        crew = OutlineCrew(inputs=config)
        inputs = {
            attr: getattr(self.state.inputs, attr)
            for attr in ['course', 'language', 'chapters_that_must_be_included', 'special_needs', 'target_audience', 'num_chapters', 'writing_style']
        }
        result = crew.crew().kickoff(inputs=inputs)
        pydantic_content = result.pydantic
        console.print("\n*-*-*-*-\n", pydantic_content, "\n*-*-*-*-\n")
        self.state.course_outline = pydantic_content
        self.update_metrics(result.token_usage)

    @listen(create_course_outline)
    def update_outline_file(self):
        """
        Add outline to 3_outline.md
        """
        outline = MarkdownWriter(self.state.titles.file_name)
        outline.write_outline(self.state.course_outline)

    @listen(update_outline_file)
    def create_content_for_each_chapter(self):
        """
        Generates content for each chapter based on input parameters.
        Returns: None.
        """
        all_chapters = self.state.course_outline.chapters
        # convert all_chapters to a dict with only title and topics
        all_chapters_dict = [{"title": chapter.title, "topics": chapter.topics} for chapter in all_chapters]
        for i, chapter in enumerate(self.state.course_outline.chapters, start=1):
            if self.state.inputs.test_mode and i >= 3: return  # test mode: only generate 2 chapters
            if i > 0: time.sleep(self.state.inputs.timeout)  # wait xx sec between 2 chapters
            console.print(
                f"\nCreating content for chapter {i}/{len(self.state.course_outline.chapters)}: {chapter.title}\n",
                style="black on yellow")

            # Initialize retry counter
            retry_count = 0
            content = {}
            while retry_count <= 5:
                # console.print(f"\n***** Retry {retry_count} for chapter {i} *****\n", style="red on white")
                config = {
                    "model": self.state.inputs.model,
                    "temperature": self.state.inputs.temperature,
                    "include_web_search": self.state.inputs.include_web_search,
                    "i": i,
                }
                crew = ChapterCrew(inputs=config)
                inputs = {
                    "course": self.state.inputs.course,
                    "language": self.state.inputs.language,
                    "special_needs": self.state.inputs.special_needs,
                    "target_audience": self.state.inputs.target_audience,
                    "writing_style": self.state.inputs.writing_style,
                    'word_length': self.state.inputs.word_length,
                    "chapter_title": chapter.title,
                    "chapter_topics": chapter.topics,
                    "all_chapters": all_chapters_dict,
                }
                result = crew.crew().kickoff(inputs=inputs)
                content = result.to_dict()

                if content != {}:
                    break
                retry_count += 1
                console.print(f"Empty content received. Retry attempt {retry_count}/5 for chapter {i}", style="red")
                time.sleep(2)  # Add small delay between retries
            if content == {}:
                console.print(f"Failed to generate content for chapter {i} after 5 attempts", style="bold red")
                continue
            # console.print(f"\n***** WHILE ENDED *****\n", style="red on white")
            console.print(f"\n*-*-* {i}/{len(self.state.course_outline.chapters)} CHAPTERS CREATED *-*-*-*-\n",
                          content, "\n*-*-*-*-\n")
            self.state.chapters.append(content)
            self.update_metrics(result.token_usage)
            # console.print(f"\n*-*-* FULL COURSE OUTPUT SO FAR *-*-*-*-\n",
            #               self.state.chapters, "\n*-*-*-*-\n")
            add_chapter = MarkdownWriter(self.state.titles.file_name)
            add_chapter.add_chapter(content)

    @listen(create_content_for_each_chapter)
    def create_exercises_for_each_chapter(self):
        """
        Generates exercises for each chapter based on input parameters.
        Returns: None.
        """
        for i, chapter in enumerate(self.state.chapters, start=1):
            time.sleep(self.state.inputs.timeout)  # wait xx sec between 2 chapters
            console.print(f"\nCreating exercises for chapter {i}/{len(self.state.chapters)}\n", style="black on yellow")
            # console.print("--*---* CHAPTER DATA --*\n", chapter, "\n--*---*--*\n")
            config = {
                "model": self.state.inputs.model,
                "temperature": self.state.inputs.temperature,
                "include_web_search": self.state.inputs.include_web_search,
                "i": i,
            }
            crew = ExercisesCrew(inputs=config)

            # if chapter["main_title"] exists
            if "main_title" in chapter:
                # Initialize retry counter
                retry_count = 0
                content = {}
                while retry_count <= 5:
                    main_title = chapter["main_title"]
                    main_content = ""
                    for topic in chapter["topics"]:
                        main_content += f"## {topic['sub_title']}\n\n{topic['content']}\n\n"
                    inputs = {
                        # "chapter": chapter,
                        "language": self.state.inputs.language,
                        "special_needs": self.state.inputs.special_needs,
                        "target_audience": self.state.inputs.target_audience,
                        "writing_style": self.state.inputs.writing_style,
                        "num_exercises": self.state.inputs.num_exercises,
                        "main_title": main_title,
                        "main_content": main_content
                    }
                    result = crew.crew().kickoff(inputs=inputs)
                    content = result.to_dict()

                    if content != {}:
                        break
                    retry_count += 1
                    console.print(f"Empty content received. Retry attempt {retry_count}/5 for chapter {i}", style="red")
                    time.sleep(2)  # Add small delay between retries

                if content == {}:
                    console.print(f"Failed to generate exercises for chapter {i} after 5 attempts", style="bold red")
                    continue

                console.print(f"\n*-*-* {i}/{len(self.state.course_outline.chapters)} EXERCISES CREATED *-*-*-*-\n",
                              content, "\n*-*-*-*-\n")
                self.state.exercises.append(content)
                self.update_metrics(result.token_usage)
                add_exercise = MarkdownWriter(self.state.titles.file_name)
                add_exercise.add_exercise(content)
        else:
            console.print(f"\n*-*-* NO EXERCISES CREATED *-*-*-*-\n", style="red on yellow")


    @listen(create_exercises_for_each_chapter)
    def create_quiz_for_each_chapter(self):
        """
        Generates exercises for each chapter based on input parameters.
        Returns: None.
        """
        for i, chapter in enumerate(self.state.chapters, start=1):
            time.sleep(self.state.inputs.timeout)  # wait xx sec between 2 chapters
            console.print(f"\nCreating quiz for chapter {i}/{len(self.state.chapters)}\n", style="black on yellow")
            # console.print("--*---* CHAPTER loop --*\n", chapter, "\n--*---*--*\n")
            # if chapter["main_title"] exists
            if "main_title" in chapter:
                # Initialize retry counter
                retry_count = 0
                content = {}
                while retry_count <= 5:
                    config = {
                        "model": self.state.inputs.model,
                        "temperature": self.state.inputs.temperature,
                        "include_web_search": self.state.inputs.include_web_search,
                        "i": i,
                    }
                    crew = QuizCrew(inputs=config)

                    main_title = chapter["main_title"]
                    main_content = ""
                    for topic in chapter["topics"]:
                        main_content += f"## {topic['sub_title']}\n\n{topic['content']}\n\n"
                    inputs = {
                        # "chapter": chapter,
                        "language": self.state.inputs.language,
                        "special_needs": self.state.inputs.special_needs,
                        "target_audience": self.state.inputs.target_audience,
                        "writing_style": self.state.inputs.writing_style,
                        "num_quizzes": self.state.inputs.num_quizzes,
                        "main_title": main_title,
                        "main_content": main_content
                    }
                    result = crew.crew().kickoff(inputs=inputs)
                    content = result.to_dict()

                    if content != {}:
                        break
                    retry_count += 1
                    console.print(f"Empty content received. Retry attempt {retry_count}/5 for chapter {i}", style="red")
                    time.sleep(2)  # Add small delay between retries

                if content == {}:
                    console.print(f"Failed to generate quiz questions for chapter {i} after 5 attempts", style="bold red")
                    continue

                console.print(f"\n*-*-* {i}/{len(self.state.course_outline.chapters)} QUIZZES CREATED *-*-*-*-\n",
                              content, "\n*-*-*-*-\n")
                self.state.quizzes.append(content)
                self.update_metrics(result.token_usage)
                add_quiz = MarkdownWriter(self.state.titles.file_name)
                add_quiz.add_quiz(content)
            else:
                console.print(f"\n*-*-* NO QUIZ QUESTIONS CREATED *-*-*-*-\n", style="red on yellow")

        # console.print(f"\nQUIZ CREATION not implemented yet\n", style="black on yellow")
        # return True

    @listen(create_quiz_for_each_chapter)
    def finish_course(self):
        console.print("Before finish ", style="black on yellow")
        console.print(f"\n{dict(self.state.inputs.metrics)}\n")
        finalize = MarkdownWriter(self.state.titles.file_name)
        finalize.finalize_course(dict(self.state.inputs.metrics))
        console.print("COURSE SUCCESSFULLY CREATED ", style="black on yellow")
        return True


def kickoff_course_flow(inputs):
    # crew_session = agentops.start_session()
    console.print("IN KICKOFF", style="red")
    console.print("inputs:", inputs)
    course = CourseFlow(inputs)
    course.plot()
    course.kickoff()
    # crew_session.end_session()


if __name__ == "__main__":
    kickoff_course_flow()
