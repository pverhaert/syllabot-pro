import os

import pandas as pd
import streamlit as st

from main import kickoff_course_flow
from models import Models
from tones import tones

# Page layout
st.set_page_config(page_title="ITF SyllaBot Pro", page_icon="assets/logo-tm.svg", layout="wide")
with open('./assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def create_folders():
    folders = ['course_latest', 'course_history']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)


def main(word_lenght=None):
    create_folders()
    # Streamlit app
    with open('assets/logo-tm.svg') as f:
        st.markdown(f'<div id="main_header">{f.read()}<p>ITF SyllaBot Pro <span>(v0.2.0)</span></p></div>',
                    unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("Input Parameters for Course Creation")
        error_container = st.empty()
        # Input parameters
        language = st.text_input("Language for this course", value="English")
        course = st.text_input("Write a course about", value="", placeholder="Short description of the topic")
        chapters_that_must_be_included = st.text_area("Chapters/topics that must be included", value="", placeholder="Optional")
        special_needs = st.text_area("Special needs to take into account?", value="", placeholder="Optional")
        target_audience = st.text_input("Target audience", value="", placeholder="Optional")
        writing_style = st.selectbox(
            "Writing Style",
            options=[t['description'] for t in tones],
            format_func=lambda x: next(t['tone'] for t in tones if t['description'] == x),
            help="Select the writing style for the course content"
        )
        model = st.selectbox("Model", options=[m['model'] for m in Models])
        st.header("Per chapter:")
        # Set default timeout value based on model selection
        default_timeout = 45 if any(x in model for x in ["groq/", ":free"]) else 0

        timeout = st.slider("Timeout between 2 chapters (sec)",
                            min_value=0, max_value=90, value=default_timeout, step=5,
                            help="Timeout between 2 API calls to avoid rate limiting"
                            )
        word_length = st.slider("Words per chapter (approximately)",
                                min_value=100, max_value=3000, value=1000, step=100,
                                help="Not all models can handle the maximum of 3.000 words per chapter")
        include_web_search = st.toggle("Include Web Search?", value=False,
                                       help="Enable or disable web search in the generated content")
        col1, col2, col3 = st.columns(3)
        with col1:
            num_chapters = st.number_input("Nr of chapters", value=5, min_value=0)
        with col2:
            num_exercises = st.number_input("Nr of Exercises/chapter", value=10, min_value=0)
        with col3:
            num_quizzes = st.number_input("Nr of Quizzes/chapter", value=10, min_value=0)
        temperature = st.slider("Temperature",
                                min_value=0.0, max_value=1.0, value=0.1, step=0.05,
                                help="Controls the randomness of the generated content. Higher values result in more random output, while lower values make the output more deterministic."
                                )
        test_mode = st.toggle("Test mode", value=False,
                              help="In test mode, only the first two chapters will be generated")

        if st.button("Generate New Content"):
            # validate language and course (required fields)
            errors = []
            if not language.strip():
                errors.append("Language is required")
            if not course.strip():
                errors.append("Course description is required")
            if errors:
                error_message = "\n".join([f"❌ {error}\n" for error in errors])
                error_container.error(error_message)
            else:
                if chapters_that_must_be_included == "":
                    chapters_that_must_be_included = "I leave it to you"
                if target_audience == "":
                    target_audience = "see writing style"
                inputs = {
                    'language': language,
                    'course': course,
                    'chapters_that_must_be_included': chapters_that_must_be_included,
                    'special_needs': special_needs,
                    'target_audience': target_audience,
                    'writing_style': writing_style,
                    'model': model,
                    'word_length': word_length,
                    'timeout': timeout,
                    'include_web_search': include_web_search,
                    'num_chapters': num_chapters,
                    'num_exercises': num_exercises,
                    'num_quizzes': num_quizzes,  # Using the same value as exercises for quiz
                    'temperature': temperature,
                    'test_mode': test_mode,
                    'serper_api_key': os.environ.get('SERPER_API_KEY', None)
                }

                # st.write("Inputs:", inputs)
                # run_flow(inputs)
                kickoff_course_flow(inputs)
                # st.snow()

    # Main content
    new_course, model_details, writing_styles, all_courses = st.tabs(
        ["New Course", "Model details", "Writing Style", "Previously Generated Courses"])

    with new_course:
        if os.path.exists('course_latest/course.md'):
            with open('course_latest/course.md', 'r', encoding='utf-8') as f:
                st.markdown(f.read(), unsafe_allow_html=True)
        else:
            st.write("No final output available yet. Generate a course to see the results.")

    with model_details:
        # Info about add/remove models
        with st.expander("📚 How to Add/Remove Models"):
            st.markdown("""
                        ##### Open the `models.py` and add or remove models as needed.

                        1. **Open** the `models.py` file in your editor
                        2. **Follow** this format to add new models:
                        ```json
                        {
                            "model": "openrouter/nvidia/llama-3.1-nemotron-70b-instruct",
                            "max_output_tokens": 131.072,
                            "price_input": 0.35,
                            "price_output": 0.4
                        }
                        ```

                        - For [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini)
                        - For [Groq models](https://console.groq.com/docs/models)
                        - For [OpenRouter models](https://openrouter.ai/models)

                        ⚠️ **Important:** always add the provider name (`gemini/`, `groq/` or `openrouter/`) before the model name!  
                        For example, for the [inflection-3-pi](https://openrouter.ai/inflection/inflection-3-pi) model on OpenRouter, 
                        the `model` key should be `openrouter/inflection/inflection-3-pi` instead of just `inflection/inflection-3-pi`.
                """)
        # Show all model details in a table (column names are Model, Max Output Tokens, Input Price, Output Price)
        table = []
        for i, model in enumerate(Models, start=1):
            table.append([model['model'], model['max_output_tokens'], f"$ {model['price_input']}",
                          f"$ {model['price_output']}"])
        # Convert the list of lists to a DataFrame
        df = pd.DataFrame(table, columns=["Model", "Max Tokens", "Input Price", "Output Price"])
        # Display the DataFrame as a table
        st.table(df)

    with writing_styles:
        # Info about add/remove tones
        with st.expander("📚 How to Add/Remove Writing Styles"):
            st.markdown("""
                                ##### Open the `tones.py` and add or remove models as needed.

                                1. **Open** the `tones.py` file in your editor
                                2. **Follow** this format to add new models:
                                ```json
                                {
                                    "tone": "Professional",
                                    "description": "Formal and technical language suitable for college students and professionals"
                                },
                                ```
                        """)
        table = []
        for i, tone in enumerate(tones, start=1):
            table.append([tone['tone'], tone['description']])
        # Convert the list of lists to a DataFrame
        df = pd.DataFrame(table, columns=["Tone", "Description"])
        # Display the DataFrame as a table
        st.table(df)

    with all_courses:
        # Read all files in course_history folder and display them in a dropdown
        course_files = [f for f in os.listdir('course_history') if os.path.isfile(os.path.join('course_history', f))]
        if len(course_files) == 0:
            st.write("No courses generated yet.")
        else:
            # Filter only .md files (.docx must not be visible in the dropdown)
            course_files = [f for f in course_files if f.endswith('.md')]
            # show all files in a reverse order
            course_files = sorted(course_files, reverse=True)
            # Get the selected md file and docx files
            selected_file_md = st.selectbox("Select a course", course_files)
            selected_file_default_docx = selected_file_md.split(".")[0] + ".docx"
            selected_file_tm_docx = selected_file_md.rsplit(".", 1)[0] + "_tm.docx"
            st.markdown("<b>Download selected file</b>", unsafe_allow_html=True)
            word, tm_word, md = st.columns(3)
            with word:
                # if the file exists, download the file in docx format
                if os.path.exists(os.path.join('course_history', selected_file_default_docx)):
                    with open(os.path.join('course_history', selected_file_default_docx), 'rb') as docx_file:
                        st.download_button('DOCX (default template)', docx_file,
                                           file_name=selected_file_default_docx,
                                           use_container_width=True,
                                           )
            with tm_word:
                # if the file exists, download the file in docx format
                if os.path.exists(os.path.join('course_history', selected_file_tm_docx)):
                    with open(os.path.join('course_history', selected_file_tm_docx), 'rb') as docx_file:
                        st.download_button('DOCX (Thomas More template)', docx_file,
                                           file_name=selected_file_tm_docx,
                                           use_container_width=True,
                                           type="primary"
                                           )
            with md:
                # download the file in Markdown format
                with open(os.path.join('course_history', selected_file_md), 'r', encoding='utf-8') as md_file:
                    st.download_button('Markdown', md_file, file_name=selected_file_md, use_container_width=True)
            # display the file content in markdown
            with open(os.path.join('course_history', selected_file_md), 'r', encoding='utf-8') as md_file:
                st.markdown(md_file.read(), unsafe_allow_html=True)


if __name__ == '__main__':
    main()
