#!/usr/bin/env -S uv run
# /// script
# requires-python = "==3.12.*"
# dependencies = [
#     "llm",
#     "llm-anthropic",
#     "click",
# ]
# ///

import subprocess
import sys
import re

import llm
import click

SYSTEM_PROMPT = """" \
Write a one-line Bash shell command to perform the following task.
Format the command using markdown syntax as follows:
```bash
COMMAND GOES HERE
```.
Use only commands built into Unix/macOS.
"""
COMMAND_RE = re.compile("```bash\n(.+)\n```")

@click.command()
@click.argument("prompt")
@click.option('--model', default="gpt-4o-mini", help="LLM model to use (any model supported by llm)")
def main(prompt, model):
    model = llm.get_model(model)
    response = model.prompt(prompt, system=SYSTEM_PROMPT)
    commands = [match[1] for match in COMMAND_RE.finditer(response.text())]

    if len(commands) == 0:
        print("Response did not contain any shell commands.")
        sys.exit(1)

    if len(commands) > 1:
        print("Response contained multiple shell commands which is not currently supported.")
        sys.exit(1)

    cmd = commands[0]
    if click.confirm(f"Run `{cmd}`?", default=True, err=True):
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")

if __name__ == "__main__":
    main()
