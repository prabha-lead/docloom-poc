# TPA Form Validator

A document validation tool that extracts and validates Third Party Authorization (TPA) forms using [DocLoom](https://elsai-core-package.optisolbusiness.com/root/elsai-docloom/) from ElsaiFoundry. Upload a TPA form PDF, and it automatically extracts key fields (agent details, generator info, signatures, etc.) and validates whether mandatory data is present — giving you a clear green/red flag instantly.

## Live Demo

[https://huggingface.co/spaces/prabha-coder/tpa-form-validator](https://huggingface.co/spaces/prabha-coder/tpa-form-validator)

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd docloom-poc
```

### 2. Install dependencies

```bash
uv sync
```

This installs all dependencies including:

| Package           | Purpose                                    |
| ----------------- | ------------------------------------------ |
| `gradio`          | Web UI for uploading and validating forms  |
| `elsai-docloom`   | Document extraction engine by ElsaiFoundry |
| `python-dotenv`   | Loads environment variables from `.env`    |
| `huggingface-hub` | Deployment to Hugging Face Spaces          |

### 3. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Update the following variable:

| Variable          | Description                                     | Required |
| ----------------- | ----------------------------------------------- | -------- |
| `DOCLOOM_API_KEY` | API key for DocLoom document extraction service | Yes      |

```env
DOCLOOM_API_KEY=your-docloom-api-key-here
```

## Run the App

```bash
uv run python main.py
```

The Gradio app will start at **http://127.0.0.1:7860**

## How It Works

1. **Upload** a TPA form (PDF) via the web UI
2. **DocLoom** extracts structured data from the document using a predefined schema
3. **Validation** checks that the following mandatory fields are present:
   - Authorized Agent Name
   - Generator Name
   - Signature
4. **Result** is displayed with a green (valid) or red (invalid) flag along with all extracted fields

## Extracted Schema Fields

| Field                                 | Type    | Description                                             |
| ------------------------------------- | ------- | ------------------------------------------------------- |
| Envelope ID                           | string  | Docusign Envelope ID                                    |
| Date                                  | string  | Date of authorization                                   |
| Authorized Agent Name                 | string  | Name of Authorized Agent                                |
| Authorized Agent Title                | string  | Title of Authorized Agent                               |
| Company Name                          | string  | Name of Company                                         |
| Telephone Number                      | string  | Telephone Number                                        |
| Complete & Sign Special Waste Profile | boolean | Complete and sign Special Waste Profile                 |
| Special Waste Profile Recertification | boolean | Complete and sign Special Waste Profile-Recertification |
| Authorize Amendments                  | boolean | Authorize amendments to Special Waste Profile           |
| Sign Contracts                        | boolean | Sign contracts to dispose and/or transport material     |
| Sign Certifications                   | boolean | Sign certifications for landfill requirements           |
| Sign Manifests                        | boolean | Sign manifests to initiate shipment                     |
| Generator Name                        | string  | Generator Name                                          |
| Generator Mailing Address             | string  | Generator Mailing Address                               |
| Generator Contact Name                | string  | Generator Contact Name                                  |
| Generator Contact Title               | string  | Title of Generator Contact                              |
| Generator Email                       | string  | Generator Email                                         |
| Signature                             | boolean | Whether a signature is present on the form              |

## Project Structure

```
docloom-poc/
├── .env                 # Environment variables (not committed)
├── .gitignore
├── main.py              # Gradio app entry point
├── pyproject.toml       # Project config & dependencies
├── requirements.txt     # For Hugging Face Spaces deployment
├── uv.lock
├── uploads/             # Uploaded TPA forms stored here
│   └── .gitkeep
└── README.md
```

## Deploy to Hugging Face Spaces

1. Login to Hugging Face:

   ```bash
   uv run python -c "from huggingface_hub import login; login()"
   ```

2. Create a Space and upload:

   ```bash
   uv run python -c "
   from huggingface_hub import HfApi
   api = HfApi()
   repo_id = 'your-username/tpa-form-validator'
   api.create_repo(repo_id=repo_id, repo_type='space', space_sdk='gradio', exist_ok=True)
   api.add_space_secret(repo_id=repo_id, key='DOCLOOM_API_KEY', value='your-api-key')
   api.upload_file(path_or_fileobj='main.py', path_in_repo='app.py', repo_id=repo_id, repo_type='space')
   api.upload_file(path_or_fileobj='requirements.txt', path_in_repo='requirements.txt', repo_id=repo_id, repo_type='space')
   "
   ```

> **Note:** The `DOCLOOM_API_KEY` is added as a secret in Hugging Face Spaces settings, not hardcoded in code.
