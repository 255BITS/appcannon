import argparse
import anthropic
import openai
import re
import time
import os
import yaml
import json
from dataclasses import dataclass
from random import randint
from ai_agent_toolbox import Toolbox, XMLParser, XMLPromptFormatter

class LLMResponseInvalid(Exception):
    """Exception raised when LLM response is invalid or cannot be parsed."""
    pass

@dataclass
class AppSettings:
    frontend: str
    backend: str
    database: str
    spec: dict
    git_repo: str
    model: str
    build_path: str
    log_file: str = None

def parse_args():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description='AppCannon - Blast off your web app development!')
    parser.add_argument('spec_file', type=str, help='Path to the YAML spec file')
    parser.add_argument('-o', '--output', dest='build_path', type=str, default='build', help='Path to build the project')
    parser.add_argument('-f', '--frontend', dest='frontend', type=str, default="htmx with tailwind.css", help='The frontend framework to use')
    parser.add_argument('-b', '--backend', dest='backend', type=str, default="flask/python3", help='Backend to use')
    parser.add_argument('-d', '--database', dest='database', type=str, default="sqlite", help='Database to use')
    parser.add_argument('-m', '--model', dest='model', type=str, default="claude-3-5-sonnet-20241022", help='AI model to use')
    parser.add_argument('-g', '--git', dest='git', type=str, default="git@github.com:your-username/your-projectname.git", help='The target git repo')
    parser.add_argument('-l', '--log', dest='log_file', type=str, default=None, help='Path to the generation log file')
    return parser.parse_args()

def read_spec_file(file_path):
    """
    Reads the YAML specification file.
    """
    with open(file_path, 'r') as file:
        spec = yaml.safe_load(file)
    return spec

def query_llm_with_retry(*args, max_retries=5, **kwargs):
    """
    Queries the LLM with retries on server errors.
    """
    base_delay = 1  # base delay in seconds
    for attempt in range(max_retries):
        try:
            return query_llm(*args, **kwargs)
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * 2 ** attempt + randint(0, 1000) / 1000
                print(f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {delay:.2f} seconds.")
                time.sleep(delay)
            else:
                print(f"All {max_retries} attempts failed. Last error: {e}")
                raise

def query_llm(system, user, model="claude-3-opus-20240229"):
    """
    Queries the specified LLM model with the given system and user prompts.
    Returns raw response text.
    """
    if model.startswith("claude"):
        client = anthropic.Anthropic()
        messages = [{"role": "user", "content": user}]
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            messages=messages,
            system=system
        )
        return response.content[0].text
    elif model.startswith("gpt-"):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=4096,
        )
        return response.choices[0].message.content
    else:
        raise ValueError(f"Unsupported model: {model}")

def log_generation(log_file, file_name, response_text):
    """
    Logs the raw LLM response to a file.
    """
    with open(log_file, 'a') as log_f:
        log_f.write(f"=== Generating {file_name} at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log_f.write(response_text)
        log_f.write("\n\n")

def save_file(build_path, file_name, contents):
    """
    Saves the file to the specified build path.
    """
    full_path = os.path.join(build_path, file_name)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(contents)
    print(f"File written to {full_path}")

def generate_app(settings):
    """
    Orchestrates the generation of the entire application using AI tools.
    """
    toolbox = Toolbox()
    parser = XMLParser(tag="use_tool")
    formatter = XMLPromptFormatter(tag="use_tool")

    # State management
    readme_content = None
    file_list = []

    # Add tools to toolbox
    def write_readme(content):
        nonlocal readme_content
        readme_content = content
        save_file(settings.build_path, "README.md", content)
        if settings.log_file:
            log_generation(settings.log_file, "README.md", content)

    toolbox.add_tool(
        name="write_readme",
        fn=write_readme,
        args={
            "content": {"type": "string", "description": "Content of the README.md file"}
        },
        description="Writes the project README file"
    )

    def provide_file_list(files):
        nonlocal file_list
        file_list = files.split(",")

    toolbox.add_tool(
        name="provide_file_list",
        fn=provide_file_list,
        args={
            "files": {"type": "string", "description": "List of project files(comma separated)"}
        },
        description="Provides the list of files to generate"
    )

    def write_file(path, content):
        save_file(settings.build_path, path, content)
        if settings.log_file:
            log_generation(settings.log_file, path, content)

    toolbox.add_tool(
        name="write_file",
        fn=write_file,
        args={
            "path": {"type": "string", "description": "File path"},
            "content": {"type": "string", "description": "File content"}
        },
        description="Writes a file to the project"
    )

    # Generate README
    system = (
        "You are a skilled AI that specializes in web app creation. Generate a README using the write_readme tool.\n"
        f"Project Specs:\n{yaml.dump(settings.spec)}\n"
        f"Frontend: {settings.frontend}\nBackend: {settings.backend}\nDatabase: {settings.database}\n"
        "Include sections: Introduction, Usage, Files, Methods, Models, CSS, JS, Notes.\n"
    )
    system += formatter.usage_prompt(toolbox)
    
    user = "Create a comprehensive README.md for the described application."
    response_text = query_llm_with_retry(system, user, model=settings.model)
    for event in parser.parse(response_text):
        toolbox.use(event)

    if not readme_content:
        raise LLMResponseInvalid("README generation failed")

    # Generate file list
    system = (
        "Analyze the README and list project files using provide_file_list tool.\n"
        "Include only text/code files (no binaries or generated files).\n"
    )
    system += formatter.usage_prompt(toolbox)
    
    user = f"README content:\n{readme_content}\n\nList the project files:"
    response_text = query_llm_with_retry(system, user, model=settings.model)
    for event in parser.parse(response_text):
        toolbox.use(event)

    if not file_list:
        raise LLMResponseInvalid("File list generation failed")

    # Generate individual files
    for file_name in file_list:
        system = (
            f"Generate code for {file_name} using write_file tool.\n"
            f"Tech stack: {settings.frontend}, {settings.backend}, {settings.database}\n"
        )
        system += formatter.usage_prompt(toolbox)
        print("Generating with", system)
        print("---")
        
        user = f"README:\n{readme_content}\n\nCreate the {file_name} file:"
        print("User prompt", user)
        print("+-+")
        response_text = query_llm_with_retry(system, user, model=settings.model)
        print("response text", response_text)
        print("+++")
        for event in parser.parse(response_text):
            toolbox.use(event)

def main():
    args = parse_args()
    spec = read_spec_file(args.spec_file)
    settings = AppSettings(
        frontend=args.frontend,
        backend=args.backend,
        database=args.database,
        spec=spec,
        git_repo=args.git,
        model=args.model,
        build_path=args.build_path,
        log_file=args.log_file
    )
    generate_app(settings)

if __name__ == '__main__':
    main()
