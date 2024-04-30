import argparse
import anthropic
import re
import time
import os
import yaml
import json
from dataclasses import dataclass
from random import randint

@dataclass
class AppSettings:
    frontend: str
    backend: str
    database: str
    spec: dict
    git_repo: str

@dataclass
class GeneratedApp:
    files: dict

def parse_args():
    parser = argparse.ArgumentParser(description='AppCannon - Blast off your web app development!')
    parser.add_argument('spec_file', type=str, help='Path to the YAML spec file')
    parser.add_argument('build_path', type=str, default='build', help='Path to build the project')
    parser.add_argument('-frontend', dest='frontend', type=str, default="htmx with tailwind.css", help='The frontend framework to use')
    parser.add_argument('-backend', dest='backend', type=str, default="flask/python3", help='Backend to use')
    parser.add_argument('-database', dest='database', type=str, default="sqlite", help='Database to use')
    parser.add_argument('-git', dest='git', type=str, default="git@github.com:your-username/your-projectname.git", help='The target git repo')
    return parser.parse_args()

def read_spec_file(file_path):
    with open(file_path, 'r') as file:
        spec = yaml.safe_load(file)
    return spec

def query_llm_with_retry(*args, max_retries=5, **kwargs):
    base_delay = 1  # base delay in seconds
    for attempt in range(max_retries):
        try:
            # Attempt the function call
            return query_llm(*args, **kwargs)
        except anthropic.InternalServerError as e:
            if attempt < max_retries - 1:
                # Calculate the delay with exponential backoff and add jitter
                delay = base_delay * 2 ** attempt + randint(0, 1000) / 1000
                print(f"Attempt {attempt + 1}/{max_retries} failed due to server overload: {e}. Retrying in {delay:.2f} seconds.")
                time.sleep(delay)
            else:
                # Log the last failure after all retries have been exhausted
                print(f"All {max_retries} attempts failed due to server overload. Last error: {e}")
                raise
        else:
            break

def query_llm(system, user, format="raw", startblock=None):
    client = anthropic.Anthropic()
    messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user
                    }]
            }
        ]

    model = "claude-3-opus-20240229"
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=messages,
    )
    text = message.content[0].text
    if startblock:
        pattern = rf'{re.escape(startblock)}\s*(.*?)\s*```'
        re_match = re.search(pattern, text, re.DOTALL)
        if re_match:
            content = re_match.group(1)
            if format == "json":
                return json.loads(content)
            else:
                return content
        else:
            print("--", content)
            raise LLMResponseInvalid()
    if format == "raw":
        return text

def generate_readme(settings):
    print("Generating README.md")
    system = f"""You are a skilled AI that specializes in webapp creation.
Generate a README for an application that matches this specification:
<yaml webapp_specification=true>
{yaml.dump(settings.spec)}
</yaml>
Include the following sections:
* Introduction
* Usage
* Files
* Methods
* Models
* Available CSS styles
* Available JS functions
* Additional notes
"""

    user = f"""
In this project we are going to use:
* Frontend framework: {settings.frontend}
* Backend framework: {settings.backend}
* Database: {settings.database}
* Git repo: {settings.git_repo}

Your response should be markdown.
    """
    generated = query_llm_with_retry(system, user)
    return generated

def generate_files(readme):
    system = f"""Given an unstructured README that lists files associated with a project, output the list of files in a format that fits a python `List[str]`. Your output should be in markdown with a "```json" block."""
    user = f"""Extract the files in this project:
```markdown
{readme}
```

Skip binary files, this should be a list of text, code or markup files. Do not include folder paths, just the files with their full path.
"""
    generated = query_llm_with_retry(system, user, format='json', startblock="```json")
    print("Generating these files:", generated)
    return generated

def generate_file(settings, readme, file):
    print("Generating ", file)
    system = f"""You are a skilled AI that specializes in webapp creation. Generate a file that matches the readme description."""
    user = f"""Create a file called {file} that matches the description in this readme:
```markdown
{readme}
```

Your response should be markdown with a "```" code block containing the file content. Make the file adhere to the specifications and write initial code that works.
"""
    generated = query_llm_with_retry(system, user, format='code', startblock="```")
    return generated

def generate_app(settings):
    readme = generate_readme(settings)
    generated_file_list = generate_files(readme)
    files = { "README.md": readme }
    for file in generated_file_list:
        built = generate_file(settings, readme, file)
        files[file] = built
    return GeneratedApp(files = files)

def save_generated_app(build_path, app):
    for file, contents in app.files.items():
        # Construct the full path for the file
        full_path = os.path.join(build_path, file)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write the contents to the file
        with open(full_path, 'w') as f:
            f.write(contents)
        print(f"File written to {full_path}")

def main():
    args = parse_args()
    spec = read_spec_file(args.spec_file)
    settings = AppSettings(frontend = args.frontend, backend = args.backend, database = args.database, spec = spec, git_repo = args.git)
    generated_app = generate_app(settings)
    save_generated_app(args.build_path, generated_app)

if __name__ == '__main__':
    main()
