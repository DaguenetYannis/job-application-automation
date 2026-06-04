# Local Job Application Automation System

This project is a local, VSCode-friendly Python system for preparing job application packets. The long-term goal is to automate the repeatable parts of applying to jobs: storing the pasted job description, parsing it, selecting relevant examples and skill blocks, generating tailored LaTeX CV and cover letter files, reviewing them, compiling PDFs, and updating an application tracker.

Milestone 1 implements only the local foundation. It does not call the OpenAI API, does not generate real AI content, and does not compile LaTeX.

## Current Milestone 1 Capabilities

- Collects only three user fields: job title, optional company, and pasted job description.
- Creates a unique application folder automatically under `applications/`.
- Saves `input.json`, `raw_job_description.txt`, `parsed_job.json`, `selected_context.json`, and `generation_plan.json`.
- Creates output folders for future CV, cover letter, and PDF artifacts.
- Performs minimal language detection for French, English, or unknown job descriptions.
- Updates `tracker.csv` automatically, creating it if missing.
- Provides explicit placeholder classes for later milestones.

## Future Roadmap

1. Parse job descriptions into structured requirements.
2. Classify role types.
3. Select relevant CV examples, cover letter examples, skill blocks, and templates.
4. Build compact prompts for the OpenAI API.
5. Generate tailored CV and cover letter LaTeX.
6. Run an AI reviewer pass and revise documents.
7. Compile PDFs with `lualatex` or `xelatex`.
8. Produce a final application packet.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Tests

```powershell
pytest
```

## Create A New Application

```powershell
python main.py new
```

Enter the job title, optionally enter the company, then paste the job description. Finish multiline input with `Ctrl+Z` then `Enter` on Windows, or `Ctrl+D` on macOS/Linux.

The system creates an application folder and appends a row to `tracker.csv`.

## Where To Add Materials

- Previous CV examples: `data/examples/cvs/`
- Previous cover letter examples: `data/examples/cover_letters/`
- LaTeX CV templates: `data/templates/cv/`
- LaTeX cover letter templates: `data/templates/cover_letter/`
- French skill blocks: `data/skill_blocks/fr/`
- English skill blocks: `data/skill_blocks/en/`
- Role rules and profiles: `data/role_profiles/`
- Candidate profile: `data/profile/candidate_profile.yaml`

CV examples, cover letter examples, and role profiles are split into these role-category folders:

- `01_data_analyst/`
- `02_bi_reporting_analytics/`
- `03_public_policy_statistics/`
- `04_economist_policy_analyst/`
- `05_climate_transition_sustainability/`
- `06_industrial_policy_competition/`
- `07_research_data_science/`
- `08_public_sector_consulting/`
- `09_international_organizations/`

## Future API Integration

Future milestones will read `OPENAI_API_KEY` from the environment. ChatGPT Plus does not automatically provide API access; API usage requires an OpenAI API account, billing setup where applicable, and a valid API key.

Create a local `.env` file based on `.env.example`:

```text
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env`. It is ignored by git because it may contain secrets.
