import datetime
import os

from common.typings import Titles


class PrepareFiles:

    def __init__(self, titles: Titles, inputs):
        self.titles = titles
        self.inputs = inputs
        self.latest_directory = "course_latest"
        self.latest_files = [
            '1_title.md',
            '2_metrics.md',
            '3_outline.md',
            '4_course_content.md',
            '5_exercises.md',
            '6_quiz.md'
        ]

    def make_files(self):
        # delete all files in the latest_ directory
        for file in os.listdir(self.latest_directory):
            os.remove(os.path.join('course_latest', file))
        # Create files in the latest_ directory
        for file in self.latest_files:
            with open(os.path.join(self.latest_directory, file), 'w', encoding='utf-8') as f:
                f.write("")
        # Add title to 1_title.md
        with open(os.path.join(self.latest_directory, '1_title.md'), 'w', encoding='utf-8') as f:
            f.write(f"# {self.titles.course_main_title}\n")
        # Add metrics template to 2_metrics.md
        metrics = [
            "___\n",
            f"## Course Generation Summary\n\n",
            f"### Input Parameters\n",
            f"- 📚 **Course Topic:** <span style='color: red'>{self.inputs.course}</span>\n",
            f"- 🗣️ **Language:** <span style='color: red'>{self.inputs.language}</span>\n",
            f"- 🌟 **Special Requirements:** <span style='color: red'>{self.inputs.special_needs}</span>\n",
            f"- 👥 **Intended For:** <span style='color: red'>{self.inputs.target_audience}</span>\n",
            f"- ✍️ **Writing Style:** <span style='color: red'>{self.inputs.writing_style}</span>\n\n",
            "### Technical Settings\n",
            f"- 🤖 **AI Model:** <span style='color: red'>{self.inputs.model}</span>\n",
            f"- 🌡️ **Creativity Level:** <span style='color: red'>{self.inputs.temperature}</span>\n\n",
            "### Course Structure\n",
            f"- 📑 **Chapters:** <span style='color: red'>{self.inputs.num_chapters}</span>\n",
            f"- 📝 **Words per Chapter:** <span style='color: red'>{self.inputs.word_length}</span>\n",
            f"- ✏️ **Exercises per Chapter:** <span style='color: red'>{self.inputs.num_exercises}</span>\n",
            f"- ❓ **Quiz Questions per Chapter:** <span style='color: red'>{self.inputs.num_quizzes}</span>\n\n",
            "### Generation Results\n",
            f"- 🔢 **Total Tokens Used:** <span style='color: red'>%%total_tokens%%</span>\n",
            f"- └─ 📤 **Prompt Tokens:** <span style='color: red'>%%prompt_tokens%%</span>\n",
            f"- └─ 📥 **Completion Tokens:** <span style='color: red'>%%completion_tokens%%</span>\n",
            f"- ✅ **Successful API Calls:** <span style='color: red'>%%successful_requests%%</span>\n",
            f"- ⏱️ **Generation Time:** <span style='color: red'>%%elapsed_time%%</span>\n",
            f"- 📅 **Generated on:** <span style='color: red'>{datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span>\n\n",
            f"💡 *Generated using [SyllaBot Pro](https://github.com/pverhaert/syllabot-pro) - An AI-powered course builder*\n\n"
            "___\n\n"
        ]
        with open(os.path.join(self.latest_directory, '2_metrics.md'), 'a', encoding='utf-8') as f:
            f.writelines(metrics)
        # Add course description title to 3_course_content.md
        with open(os.path.join(self.latest_directory, '4_course_content.md'), 'a', encoding='utf-8') as f:
            f.write(f"## {self.titles.course_content_title}\n\n")
        # Add exercises title to 4_exercises.md
        with open(os.path.join(self.latest_directory, '5_exercises.md'), 'a', encoding='utf-8') as f:
            f.write(f"## {self.titles.exercises_title}\n\n")
        # Add quiz title to 5_quiz.md
        with open(os.path.join(self.latest_directory, '6_quiz.md'), 'a', encoding='utf-8') as f:
            f.write(f"## Quiz\n\n")
        # Create empy course.md file
        with open(os.path.join(self.latest_directory, 'course.md'), 'a', encoding='utf-8') as f:
            f.write("")
