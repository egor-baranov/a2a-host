# Introduction

A python package that is making A2A host creation and deployment easy


# Examples

```python
import click
import os

from hosts.agent import A2AHost
from google.adk.models.lite_llm import LiteLlm


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10008)
def main(host, port):
    model = os.getenv("LLM_NAME", "gpt-4o")
    api_key = os.getenv("LLM_API_KEY", "")
    api_base = os.getenv("LLM_URL", "https://api.openai.com/v1/chat/completions")

    llm: LiteLlm = LiteLlm(
        model=model,
        api_base=api_base,
        api_key=api_key
    )

    A2AHost(host, port, llm=llm)


if __name__ == "__main__":
    main()

```
