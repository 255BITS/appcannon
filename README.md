# 🚀 AppCannon

AppCannon is a powerful tool that generates full-stack web applications from a simple YAML specification file. It leverages the power of Large Language Models (LLMs) to create a complete application with a frontend, backend, and database, all with just a single command.

## Features

- 💪 Generates a complete web app from a concise YAML spec file
- 🎨 Supports any frontend
- 🔧 Generates backend code in any language
- 📊 Integrates with all databases
- 📝 Creates a comprehensive README.md file for the generated app
- 🗂️ Organizes the generated code into a clean project structure
- ⚙️  Supports multiple models including claude-3-5-sonnet-2024-0620 and gpt-4o

## Installation

1. Clone the AppCannon repository:
   ```
   git clone https://github.com/255BITS/appcannon.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your API key as an environment variable:
   ```
   export OPENAI_API_KEY=your_openai_api_key_here
   # or if using Claude
   export ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Usage

To generate a web app using AppCannon, run the following command:

```
python appcannon.py spec_file.yaml output_directory [options]
```

- `spec_file.yaml`: The path to the YAML specification file for your app.
- `output_directory`: The directory where the generated app files will be saved.

Optional arguments:
- `-f` or `--frontend`: The frontend framework to use (default: "htmx with tailwind.css").
- `-b` or `--backend`: The backend framework to use (default: "flask/python3").
- `-d` or `--database`: The database to use (default: "sqlite").
- `-g` or `--git`: The target Git repository for the generated app.
- `-m` or `--model`: The model name to use for generation.
- `-l` or `--log`: Optional. Specify a log file to record the generation process.

## Example

Here's an example of how to use AppCannon:

```
python appcannon.py examples/todo_app.yaml generated_apps/todo_app -frontend "react" -backend "node/express" -database "mongodb" -model "claude-3-5-sonnet-20240620"
```

This command will generate a todo app using React for the frontend, Node.js with Express for the backend, and MongoDB as the database. The generated app files will be saved in the `generated_apps/todo_app` directory.

## Changelog

* Nov 9 2024 - Added CLI flags, support for Claude Sonnet 3.5 model
* May 13 2024 - GPT4o support
* Apr 27 2024 - Initial release

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

AppCannon is dual-licensed under both the MIT License and a Commercial License.

### MIT License

The MIT License is a permissive open-source license that allows you to freely use, modify, and distribute AppCannon for any purpose, subject to the terms and conditions of the license. Under this license, AppCannon is provided "as is" without warranty of any kind.

See the [LICENSE-MIT](LICENSE-MIT) file for the full text of the MIT License.

### Commercial License

For users or organizations generating revenue over $10,000 per month or who have raised funding, we request that you purchase a Commercial License to support the ongoing development and maintenance of AppCannon.

The Commercial License provides the following additional benefits:

- Priority support and assistance from the AppCannon team
- Custom feature development and integration services
- Legal assurances and indemnification for the use of AppCannon
- The ability to influence the project roadmap and prioritization

To inquire about purchasing a Commercial License, please contact us at [martyn+sales@255bits.com](mailto:martyn+sales@255bits.com).

We appreciate your support in keeping AppCannon a sustainable open-source project!

*Part of the [255labs.xyz](https://255labs.xyz) toolkit for AI-first development.*
