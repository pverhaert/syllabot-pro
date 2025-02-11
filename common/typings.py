from typing import List

from pydantic import BaseModel, Field


# Title outline -----------------------------------------------------------------------------------------
class Titles(BaseModel):
    file_name: str = Field(description="Filename for the final files (with underscores)")
    course_main_title: str = Field(description="Main title for the course")
    course_content_title: str = Field(description="'Course Content' (translated to the selected language")
    exercises_title: str = Field(description="'Exercises' (translated to the selected language")


# Course outline ---------------------------------------------------------------------------------------
class ChapterOutlines(BaseModel):
    title: str = Field(description="The title of the chapter")
    topics: List[str] = Field(
        default_factory=list,
        description="List of topics covered in the chapter"
    )


class Resource(BaseModel):
    title: str = Field(description="The title of the resource")
    url: str = Field(description="The URL of the resource")
    description: str = Field(description="A brief description of the resource")


class CourseOutline(BaseModel):
    course_description_title: str = Field(description="The title for the course description section")
    course_description: str = Field(description="A detailed description of the course")
    outline_title: str = Field(description="The title for the course outline section")
    chapters: List[ChapterOutlines] = Field(
        default_factory=list,
        description="List of chapter outlines in the course"
    )
    resources_title: str = Field(description="The title for the resources section")
    resources: List[Resource] = Field(
        default_factory=list,
        description="List of resources for the course"
    )
    learning_outcomes_title: str = Field(description="The title for the learning outcomes section")
    learning_outcomes: str = Field(description="A description of the learning outcomes for the course")

# Content for one chapter ---------------------------------------------------------------------------------------
class ChapterContent(BaseModel):
    sub_title: str = ""
    content: str = ""


class OneChapter(BaseModel):
    main_title: str = ""
    topics: List[ChapterContent] = []

# Content for exercises ---------------------------------------------------------------------------------------
class OneExercise(BaseModel):
    title: str = ""
    question: str = ""
    solution: str = ""
    explanation: str = ""


class ExercisesContent(BaseModel):
    main_title: str = ""
    exercises: List[OneExercise] = []


# Content for quiz ---------------------------------------------------------------------------------------
class OneQuestion(BaseModel):
    title: str = ""
    question: str = ""
    answers: List[str] = []
    correct_answer: str = ""
    explanation: str = ""


class QuizContent(BaseModel):
    main_title: str = ""
    quizzes: List[OneQuestion] =[]

# Content for quiz ---------------------------------------------------------------------------------------
class OneQuestionOLD(BaseModel):
    title: str = Field(default="", description="Title of the question")
    question: str = Field(default="", description="The question")
    answers: List[str] = Field(
        default_factory=list,
        description="A list of possible answers"
    )
    correct_answer: str = Field(default="", description="The correct answer")
    explanation: str = Field(default="", description="Explanation of the correct answer")


class QuizContentOld(BaseModel):
    main_title: str = Field(ddefault="", escription="Main title of the quiz section")
    quizzes: List[OneQuestion] = Field(
        default_factory=list,
        description="A list of questions with a title, a question, a list of possible answers, the correct answer and an explanation of the correct answer"
    )


# #################################################################################################################

#  Chapter outline
# class Chapter(BaseModel):
#     title: str
#     content: str
#
#
# class LearningOutcome(BaseModel):
#     title: str
#     description: str
