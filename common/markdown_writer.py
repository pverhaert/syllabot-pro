import shutil
from pathlib import Path

import pypandoc
from rich.console import Console

from common.typings import CourseOutline, ExercisesContent, QuizContent, OneChapter

console = Console()


class MarkdownWriter:
    """Handles markdown file operations and conversions for course content."""

    LATEST_FILES = [
        '1_title.md',
        '2_metrics.md',
        '3_outline.md',
        '4_course_content.md',
        '5_exercises.md',
        '6_quiz.md'
    ]

    def __init__(self, output_file_name: str):
        self.output_file_name = output_file_name
        self.course_dir = Path("course_history")
        self.output_latest_dir = Path("course_latest")
        self.final_course = self.course_dir / output_file_name
        self.course_file = "course.md"

        # Ensure directories exist
        self.course_dir.mkdir(exist_ok=True)
        self.output_latest_dir.mkdir(exist_ok=True)

    def _write_section(self, file, title: str, content: str) -> None:
        """Helper method to write a section with title and content."""
        if content:
            file.write(f"## {title}\n\n{content}\n\n")

    def _rename_txt_to_json(self) -> None:
        """
        Rename all .txt files to .json files in the course_latest directory.
        Only changes the extension, not the content.
        """
        for file_path in self.output_latest_dir.glob('*.txt'):
            new_name = file_path.with_suffix('.json')
            file_path.rename(new_name)

    def write_outline(self, course_outline: CourseOutline) -> None:
        """Writes course outline to markdown file with proper formatting."""
        console.print(course_outline)

        outline_path = self.output_latest_dir / "3_outline.md"

        with outline_path.open('w', encoding='utf-8') as f:
            # Write course description
            self._write_section(f,
                                course_outline.course_description_title,
                                course_outline.course_description)

            # Write outline
            f.write(f"## {course_outline.outline_title}\n\n")
            for chapter in course_outline.chapters:
                f.write(f"### {chapter.title}\n\n")
                f.write("\n".join(f"- {topic}" for topic in chapter.topics))
                f.write("\n\n")

            # Write resources if available
            if course_outline.resources_title:
                f.write(f"## {course_outline.resources_title}\n\n")
                for resource in course_outline.resources:
                    f.write(f"- [{resource.title}]({resource.url}):\n"
                            f"  {resource.description}\n")
                f.write("\n")

            # Write learning outcomes if available
            if course_outline.learning_outcomes_title:
                learning_outcomes_content = course_outline.learning_outcomes.replace("\\n", "\n")
                self._write_section(f,
                                    course_outline.learning_outcomes_title,
                                    learning_outcomes_content)

        self.combine_files()

    def add_chapter(self, chapter_dict: dict) -> None:
        content_path = self.output_latest_dir / "4_course_content.md"

        with content_path.open('a', encoding='utf-8') as f:
            if chapter_dict:
                f.write(f"### {chapter_dict['main_title']}\n\n")

                for topic in chapter_dict['topics']:
                    # Replace "\\n" with "\n" in topic content for proper new-lines
                    topic_content = topic['content'].replace("\\n", "\n")
                    f.write(f"\n#### {topic['sub_title']}\n")
                    f.write(f"\n{topic_content}\n\n")

                f.write(f"\n\n---\n\n")
            else:
                f.write("\n**OEPS!**\nTHERE IS SOMETHING WRONG WITH THIS CHAPTER :-(\n\n")
                f.write(f"\n\n---\n\n")

        self.combine_files()

    # def add_chapter(self, chapter: 'OneChapter') -> None:
    #     content_path = self.output_latest_dir / "4_course_content.md"
    #
    #     with content_path.open('a', encoding='utf-8') as f:
    #         if chapter:
    #             f.write(f"### {chapter.main_title}\n\n")
    #
    #             for topic in chapter.topics:
    #                 # Replace "\\n" with "\n" in topic content for proper new-lines
    #                 topic_content = topic.content.replace("\\n", "\n")
    #                 f.write(f"\n#### {topic.sub_title}\n")
    #                 f.write(f"\n{topic_content}\n\n")
    #
    #             f.write(f"\n\n---\n\n")
    #         else:
    #             f.write("\n**OEPS!**\nTHERE IS SOMETHING WRONG WITH THIS CHAPTER :-(\n\n")
    #             f.write(f"\n\n---\n\n")
    #
    #     self.combine_files()

    def add_exercise(self, exercises: dict) -> None:
        content_path = self.output_latest_dir / "5_exercises.md"
        with content_path.open('a', encoding='utf-8') as f:
            if exercises:
                f.write(f"### {exercises.get('main_title', 'Exercises')}\n\n")
                # Loop through each exercise in the exercises list from the dict
                for exercise in exercises.get('exercises', []):
                    question_content = exercise.get('question', '').replace("\\n", "\n")
                    solution_content = exercise.get('solution', '').replace("\\n", "\n")
                    explanation_content = exercise.get('explanation', '').replace("\\n", "\n")
                    title_content = exercise.get('title', '').replace("$", "*")

                    f.write(f"#### {title_content}\n\n")
                    f.write(f"{question_content}\n\n")
                    f.write(f"{solution_content}\n\n")
                    f.write(f"{explanation_content}\n\n")
                f.write(f"\n\n---\n\n")
            else:
                f.write("\n**OEPS!**\nTHERE IS SOMETHING WRONG WITH THIS CHAPTER :-(\n\n")
                f.write(f"\n\n---\n\n")
        self.combine_files()

    # def add_exercise(self, exercises: ExercisesContent) -> None:
    #     content_path = self.output_latest_dir / "5_exercises.md"
    #     with content_path.open('a', encoding='utf-8') as f:
    #         if exercises:
    #             f.write(f"### {exercises.main_title}\n\n")
    #             # Loop through each exercise in the list
    #             for exercise in exercises.exercises:
    #                 question_content = exercise.question.replace("\\n", "\n")
    #                 solution_content = exercise.solution.replace("\\n", "\n")
    #                 explanation_content = exercise.explanation.replace("\\n", "\n")
    #                 title_content = exercise.title.replace("$", "*")
    #                 f.write(f"#### {title_content}\n\n")
    #                 f.write(f"{question_content}\n\n")
    #                 f.write(f"{solution_content}\n\n")
    #                 f.write(f"{explanation_content}\n\n")
    #             f.write(f"\n\n---\n\n")
    #         else:
    #             f.write("\n**OEPS!**\nTHERE IS SOMETHING WRONG WITH THIS CHAPTER :-(\n\n")
    #             f.write(f"\n\n---\n\n")
    #     self.combine_files()

    def add_quiz(self, quizzes: dict) -> None:
        content_path = self.output_latest_dir / "6_quiz.md"
        with content_path.open('a', encoding='utf-8') as f:
            if quizzes:
                f.write(f"### {quizzes.get('main_title', 'Quiz')}\n\n")
                # Loop through each quiz question in the list
                for quiz in quizzes.get('quizzes', []):
                    quiz_correct_answer = quiz.get('correct_answer', '').replace("\\n", "\n")
                    quiz_explanation = quiz.get('explanation', '').replace("\\n", "\n")
                    quiz_title = quiz.get('title', '').replace("$", "*")

                    f.write(f"#### {quiz_title}\n\n")
                    f.write(f"{quiz.get('question', '')}\n\n")

                    # Handle answers list
                    for answer in quiz.get('answers', []):
                        f.write(f"- {answer}\n")

                    f.write(f"\n\n")
                    f.write(f"{quiz_correct_answer}\n\n")
                    f.write(f"{quiz_explanation}\n\n")
                f.write(f"\n\n---\n\n")
            else:
                f.write("\n**OEPS!**\nTHERE IS SOMETHING WRONG WITH THIS QUIZ :-(\n\n")
                f.write(f"\n\n---\n\n")
        self.combine_files()

    # def add_quiz(self, quizzes: QuizContent) -> None:
    #     content_path = self.output_latest_dir / "6_quiz.md"
    #     with content_path.open('a', encoding='utf-8') as f:
    #         if quizzes:
    #             f.write(f"### {quizzes.main_title}\n\n")
    #             # Loop through each quiz question in the list
    #             for quiz in quizzes.quizzes:
    #                 # quiz_content = quiz.title.replace("\\n", "\n")
    #                 # quiz_answers = quiz.answers.replace("\\n", "\n")
    #                 quiz_correct_answer = quiz.correct_answer.replace("\\n", "\n")
    #                 quiz_explanation = quiz.explanation.replace("\\n", "\n")
    #                 quiz_title = quiz.title.replace("$", "*")
    #                 f.write(f"### {quiz_title}\n\n")
    #                 f.write(f"{quiz.question}\n\n")
    #                 for answer in quiz.answers:
    #                     f.write(f"- {answer}\n")
    #                 f.write(f"\n\n")
    #                 f.write(f"{quiz_correct_answer}\n\n")
    #                 f.write(f"{quiz_explanation}\n\n")
    #             f.write(f"\n\n---\n\n")
    #         else:
    #             f.write("\n**OEPS!**\nTHERE IS SOMETHING WRONG WITH THIS QUIZ :-(\n\n")
    #             f.write(f"\n\n---\n\n")
    #     self.combine_files()

    def finalize_course(self, metrics):
        file_path = self.output_latest_dir / "2_metrics.md"
        # Update placeholders
        time_difference = metrics["end_time"] - metrics["start_time"]
        elapsed_time = f"{time_difference.seconds // 60:02}:{time_difference.seconds % 60:02}"

        try:
            # Replace placeholders with formatted numbers
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            content = content.replace("%%total_tokens%%", f"{metrics['total_tokens']:,}".replace(',', '.'))
            content = content.replace("%%completion_tokens%%", f"{metrics['completion_tokens']:,}".replace(',', '.'))
            content = content.replace("%%prompt_tokens%%", f"{metrics['prompt_tokens']:,}".replace(',', '.'))
            content = content.replace("%%successful_requests%%", f"{metrics['successful_requests']}")
            content = content.replace("%%elapsed_time%%", str(elapsed_time))

            # Save the updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.combine_files()
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"Error updating file: {str(e)}")

    def write_course_content(self, course_chapter: OneChapter) -> None:
        """Writes course content to markdown file with proper formatting."""
        content_path = self.output_latest_dir / "4_course_content.md"
        with content_path.open('a', encoding='utf-8') as f:
            for chapter in course_chapter:
                pass

        # with content_path.open('a', encoding='utf-8') as f:
        #     for content in course_content:
        #         # Strip extra whitespace and ensure content isn't empty
        #         if content := content.strip():
        #             # Add markdown horizontal rule between sections
        #             f.write(f"\n{content}\n\n---\n")

        self.combine_files()

    def combine_files(self) -> None:
        """Combines all markdown files and converts to different formats."""
        self._rename_txt_to_json()
        output_file = self.output_latest_dir / self.course_file

        # Combine markdown files
        with output_file.open('w', encoding='utf-8') as outfile:
            for input_file in self.LATEST_FILES:
                input_path = self.output_latest_dir / input_file
                try:
                    outfile.write(input_path.read_text(encoding='utf-8'))
                except FileNotFoundError:
                    console.print(f"Warning: File {input_file} not found", style="yellow")

        # Copy to final location
        # self.final_course.write_text(output_file.read_text(encoding='utf-8'))
        shutil.copy2(output_file, self.final_course)

        # Convert to different formats
        self._convert_to_docx(output_file)

    def _convert_to_docx(self, source_file: Path) -> None:
        """Converts markdown to regular and Thomas More template DOCX."""
        try:
            base_name = str(self.final_course.with_suffix(''))  # remove extension .md
            # Regular DOCX
            pypandoc.convert_file(
                str(source_file),
                "docx",
                outputfile=f"{base_name}.docx"
            )

            # Thomas More template DOCX
            pypandoc.convert_file(
                str(source_file),
                "docx",
                outputfile=f"{base_name}_tm.docx",
                extra_args=["--reference-doc", "./course_templates/ThomasMore.docx"]
            )
        except Exception as e:
            console.print(f"Error converting to DOCX: {e}", style="red")
