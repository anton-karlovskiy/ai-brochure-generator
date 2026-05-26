import json
import sys
from openai import OpenAI
from .scraper import fetch_website_content, fetch_website_links

LINK_SELECTION_MODEL = "gpt-5-nano"
BROCHURE_MODEL = "gpt-4.1-mini"

_links_system_prompt = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

_brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""


def _get_links_user_prompt(url: str) -> str:
    prompt = (
        f"Here is the list of links on the website {url} -\n"
        "Please decide which of these are relevant web links for a brochure about the company, "
        "respond with the full https URL in JSON format.\n"
        "Do not include Terms of Service, Privacy, email links.\n\n"
        "Links (some might be relative links):\n\n"
    )
    prompt += "\n".join(fetch_website_links(url))
    return prompt


def _select_relevant_links(client: OpenAI, url: str) -> dict:
    print(f"Selecting relevant links for {url} ...", file=sys.stderr)
    response = client.chat.completions.create(
        model=LINK_SELECTION_MODEL,
        messages=[
            {"role": "system", "content": _links_system_prompt},
            {"role": "user", "content": _get_links_user_prompt(url)},
        ],
        response_format={"type": "json_object"},
    )
    links = json.loads(response.choices[0].message.content)
    print(f"Found {len(links['links'])} relevant links", file=sys.stderr)
    return links


def _fetch_all_content(client: OpenAI, url: str) -> str:
    content = fetch_website_content(url)
    relevant_links = _select_relevant_links(client, url)
    result = f"## Landing Page:\n\n{content}\n## Relevant Links:\n"
    for link in relevant_links["links"]:
        result += f"\n\n### Link: {link['type']}\n"
        result += fetch_website_content(link["url"])
    return result


def _get_brochure_user_prompt(client: OpenAI, company_name: str, url: str) -> str:
    prompt = (
        f"You are looking at a company called: {company_name}\n"
        "Here are the contents of its landing page and other relevant pages; "
        "use this information to build a short brochure of the company in markdown without code blocks.\n\n"
    )
    prompt += _fetch_all_content(client, url)
    return prompt[:5_000]


def stream_brochure(client: OpenAI, company_name: str, url: str) -> None:
    stream = client.chat.completions.create(
        model=BROCHURE_MODEL,
        messages=[
            {"role": "system", "content": _brochure_system_prompt},
            {"role": "user", "content": _get_brochure_user_prompt(client, company_name, url)},
        ],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content or ""
        print(text, end="", flush=True)
    print()
