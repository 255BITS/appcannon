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

def extract_code_block(text):
    """
    Extracts the first code block from text.
    """
    pattern = r'```(?:[\w+-]*)\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return text  # Return full text if no code block is found

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

def query_llm(system, user, format="raw", model="claude-3-opus-20240229"):
    """
    Queries the specified LLM model with the given system and user prompts.
    """
    if model.startswith("claude"):
        client = anthropic.Anthropic()
        messages = [
            {
                "role": "user",
                "content": user
            }
        ]
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            messages=messages,
            system=system
        )
        text = response.content[0].text
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
        text = response.choices[0].message.content
    else:
        raise ValueError(f"Unsupported model: {model}")

    if format == 'json':
        try:
            content = extract_code_block(text)
            processed_content = json.loads(content)
        except (json.JSONDecodeError, LLMResponseInvalid):
            try:
                processed_content = json.loads(text)
            except json.JSONDecodeError as e:
                raise LLMResponseInvalid(f"Failed to parse JSON: {e}")
    elif format == 'code':
        processed_content = extract_code_block(text)
    elif format == 'raw':
        processed_content = text
    else:
        raise ValueError(f"Unsupported format: {format}")

    return processed_content, text  # Return both processed content and raw text

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

def generate_readme(settings):
    """
    Generates and saves the README.md file based on the settings and specification.
    """
    print("Generating README.md")
    system_prompt = (
        "You are a skilled AI that specializes in web app creation."
    )
    user_prompt = (
        "Generate a README for an application that matches this specification:\n"
        f"<yaml webapp_specification=true>\n{yaml.dump(settings.spec)}\n</yaml>\n"
        "Include the following sections:\n"
        "* Introduction\n"
        "* Usage\n"
        "* Files\n"
        "* Methods\n"
        "* Models\n"
        "* Available CSS styles\n"
        "* Available JS functions\n"
        "* Additional notes\n"
        f"In this project we are going to use:\n"
        f"* Frontend framework: {settings.frontend}\n"
        f"* Backend framework: {settings.backend}\n"
        f"* Database: {settings.database}\n"
        f"* Git repo: {settings.git_repo}\n\n"
        "Your response should be markdown. On the files section, only reference custom files unique to this project. Do not include files that can be included through packages or cdns."
    )
    readme, raw_response = query_llm_with_retry(system_prompt, user_prompt, model=settings.model)
    save_file(settings.build_path, "README.md", readme)
    if settings.log_file:
        log_generation(settings.log_file, "README.md", raw_response)
    return readme

def generate_files(settings, readme):
    """
    Generates a list of files to be created based on the README content.
    """
    print("Extracting file list from README.md")
    system_prompt = (
        "Given an unstructured README that lists files associated with a project, "
        "output the list of files in JSON format that fits a Python `List[str]`. "
        "Your output should be in a markdown code block with ```json."
    )
    user_prompt = (
        f"Extract the files in this project from the following README:\n"
        "```markdown\n"
        f"{readme}\n"
        "```\n\n"
        "Skip binary files; this should be a list of text, code, or markup files. "
        "Do not include folder paths, just the files with their full path."
    )
    files, raw_response = query_llm_with_retry(
        system_prompt,
        user_prompt,
        format='json',
        model=settings.model
    )
    if settings.log_file:
        log_generation(settings.log_file, "File List", raw_response)
    print("Files to generate:", files)
    return files

def generate_file(settings, readme, file_name):
    """
    Generates the content for a single file based on the README and file name.
    """
    print(f"Generating {file_name}")
    system_prompt = (
        "You are a skilled AI that specializes in web app creation. "
        "Generate a file that matches the README description."
    )
    user_prompt = (
        f"Create a file called `{file_name}` that matches the description in this README:\n"
        "```markdown\n"
        f"{readme}\n"
        "```\n\n"
        "Your response should be a markdown code block containing the file content. "
        "Ensure the file adheres to the specifications and contains initial code that works."
    )
    file_content, raw_response = query_llm_with_retry(
        system_prompt,
        user_prompt,
        format='code',
        model=settings.model
    )
    save_file(settings.build_path, file_name, file_content)
    if settings.log_file:
        log_generation(settings.log_file, file_name, raw_response)

def generate_app(settings):
    """
    Orchestrates the generation of the entire application.
    """
    # Generate and save README.md
    readme = generate_readme(settings)
    # Extract file list from README.md
    file_list = generate_files(settings, readme)
    # Generate and save each file
    for file_name in file_list:
        generate_file(settings, readme, file_name)

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
