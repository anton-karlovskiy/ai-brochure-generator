import argparse
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from brochure import stream_brochure


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set. Add it to a .env file.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Generate a company brochure from its website.")
    parser.add_argument("company_name", help='Company name, e.g. "HuggingFace"')
    parser.add_argument("url", help="Company website URL, e.g. https://huggingface.co")
    args = parser.parse_args()

    client = OpenAI(api_key=api_key)
    stream_brochure(client, args.company_name, args.url)


if __name__ == "__main__":
    main()
