# AI Brochure Generator

Generates a markdown brochure for any company by scraping its website and using OpenAI to summarize the content. Designed for prospective clients, investors, and recruits.

## How it works

1. **Link selection** — scrapes the landing page and uses `gpt-5-nano` (JSON mode) to identify the most relevant links (About, Careers, Products, etc.), filtering out noise like privacy/ToS pages.
2. **Brochure generation** — fetches content from the selected pages, assembles a prompt, and streams a markdown brochure via `gpt-4.1-mini`.

The scraper strips scripts, styles, and images, keeping only readable text. Total prompt content is capped at 5,000 characters.

## Project structure

```
brochure/
  scraper.py     # HTML fetching and text extraction (BeautifulSoup)
  generator.py   # Link selection and brochure generation (OpenAI)
main.py          # CLI entry point
```

## Setup

```bash
uv sync
```

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

## Usage

```bash
uv run main.py "HuggingFace" https://huggingface.co
```

Output streams to stdout as markdown. Redirect to a file to save:

```bash
uv run main.py "Anthropic" https://anthropic.com > brochure.md
```
