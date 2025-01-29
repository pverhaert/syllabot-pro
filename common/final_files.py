import datetime
import os
import shutil
import pypandoc

class FinalFiles:
    def __init__(self, final_file_name):
        self.outline = "course_latest/1_outline.md"
        self.course_content = "course_latest/2_course_content.md"
        self.exercises = "course_latest/3_exercises.md"
        self.quiz = "course_latest/4_quiz.md"
        self.course = "course_latest/course.md"

        self.final_file_name = final_file_name
        # Create the final path without extension
        self.final_course = os.path.join("course_history", f"{self.final_file_name}")

    def merge_files(self):
        final_markdown = ""

        # Read and merge files
        files_to_check = [self.outline, self.course_content, self.exercises, self.quiz]
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    final_markdown += f.read()
        # Join content with double newlines to ensure proper spacing
        # final_content = "\n\n".join(final_markdown)
        final_content = final_markdown

        # Ensure proper spacing between bullets and headers
        # final_content = self.fix_markdown_formatting(final_content)

        # Write merged content to course.md
        with open(self.course, 'w', encoding='utf-8') as f:
            f.write(final_content)

        # print(f"Course file: {self.course}")
        # print(f"Final course path: {self.final_course}")

        # Save markdown version
        # final_markdown_file = self.final_file_name
        with open(self.final_course, 'w', encoding='utf-8') as f:
            f.write(final_content)

        # Convert to regular DOCX
        pypandoc.convert_file(
            self.course,
            "docx",
            outputfile=f"{self.final_course}.docx"
        )

        # Convert to Thomas More template DOCX
        pypandoc.convert_file(
            self.course,
            "docx",
            outputfile=f"{self.final_course}_tm.docx",
            extra_args=["--reference-doc", "./course_templates/ThomasMore.docx"]
        )

    def fix_markdown_formatting(self, content):
        # Add newline before headers
        # content = content.replace("\n#", "\n\n#")
        return content

