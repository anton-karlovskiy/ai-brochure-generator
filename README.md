# AI Brochure Generator

Generates a markdown brochure for any company by scraping its website and using OpenAI to summarize the content.

It fetches the landing page, selects relevant links (About, Careers, etc.) using `gpt-5-nano`, then streams a brochure via `gpt-4.1-mini`.

## Setup

```bash
uv venv
uv pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

## Usage

```bash
uv run main.py "HuggingFace" https://huggingface.co
```

Output is streamed to stdout as markdown.
