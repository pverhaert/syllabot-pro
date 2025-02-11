# SyllaBot Pro with CrewAI

This repository facilitates the creation of educational courses using [CrewAI](https://crew.ai/), optimized for programming language instruction.

## Project Structure
- `course_latest`: Contains individual files of the most recently generated course.
- `course_history`: Stores all generated courses in three formats (two Word formats and one Markdown format).

> [!CAUTION]
> - If course creation fails, try lowering the word count limit or using a different LLM.
> - Always verify results, as LLMs can produce inaccurate information.
> - Generate multiple courses for content variety.
> - Test different models to determine optimal performance.
> - For non-English content, verify the model’s language capabilities.
> - Use generated content as a foundation for further course development.

## Requirements
- [Git](https://git-scm.com/)
- [Python](https://www.python.org) version `3.10.x` or `3.11.x` (Verify with `python -V`).

## Getting Started

### Clone the repository:
   ```bash
   git clone https://github.com/pverhaert/syllabot-pro
   ```

> [!NOTE]
> Please be patient as the initial setup may take 10 or more minutes to complete.

### Windows Setup
Run `install.bat` to:
- Create a virtual environment.
- Install dependencies.
- Generate `.env` file.
- Create `models.py` file.



### Linux/macOS Setup
1. Create and activate a virtual environment named `.venv`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`.
4. Copy `models.example.py` to `models.py`.

## API Configuration

### Required APIs
- **Serper API**: Used for web source discovery.
  - Free tier: 2,500 API calls.
  - Get key at [Serper API](https://serper.dev).
  - Add to `.env`: `SERPER_API_KEY=your_key`.

- **Groq API**: Required for `groq/...` models.
  - Free service.
  - Register at [Groq Console](https://groq.com).
  - Add to `.env`: `GROQ_API_KEY=your_key`.

- **Gemini API**: Required for `gemini/...` models.
  - Get key at [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key).
  - Access via Google AI Studio.
  - Add to `.env`: `GEMINI_API_KEY=your_key`.

### Optional APIs
- **OpenRouter API**: Required for `openrouter/...` models.
  - Provides access to various AI models.
  - Register at [OpenRouter](https://openrouter.com).
  - Add to `.env`: `OPENROUTER_API_KEY=your_key`.

### Example `.env` file:
```
SERPER_API_KEY=
# AGENTOPS_API_KEY=  # not implemented yet

GROQ_API_KEY=
GEMINI_API_KEY=
OPENROUTER_API_KEY=

# Disable telemetry
OTEL_SDK_DISABLED=true
```

## Running the Application
- **Windows**: Execute `run.bat`.
- **Linux/macOS**:
  1. Activate the virtual environment.
  2. Run:
     ```bash
     streamlit run main.py
     ```

## Configuration Options
- **Course Language**: Specify target language.
- **Course Topic**: Define course subject.
- **Special Requirements**: Optional specific topics to cover.
- **Target Audience**: Optional audience specification.
- **Model Selection**: Choose AI model.
- **Writing Style**: Select from predefined styles.
- **Technical Settings**:
  - Chapter timeout (seconds): Timeout between 2 API calls to avoid rate limiting
  - Words per chapter.
  - Number of chapters.
  - Exercises per chapter.
  - Quiz questions per chapter.
  - Temperature (0-1): The higher the temperature, the more diverse the course will be, but also the more hallucination you can expect.
  - Test mode option: When enabled, only the first two chapters are generated

## Accessing Generated Content
Generated courses are stored in `course_history` in both Markdown and Word formats.

> [!TIP]
> For Markdown viewing:
> - Install the [Markdown Viewer](https://chromewebstore.google.com/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk) extension to view the course files in your browser.
> - Open the extension settings:
>   - **Origins**: enable all options to allow the extension to [have access to your local files](https://github.com/simov/markdown-viewer?tab=readme-ov-file#manage-origins).
>   - **Settings**: enable all options in the **Content** section.
> - Drag and drop the Markdown file `course_latest/course.md` into your browser to watch the course generation in real-time.
