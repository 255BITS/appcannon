# 🚀 AppCannon

AppCannon is a powerful tool that generates full-stack web applications from a simple YAML specification file. It leverages the power of Large Language Models (LLMs) to create a complete application with a frontend, backend, and database, all with just a single command.

## Features

- 💪 Generates a complete web app from a concise YAML spec file
- 🎨 Supports any frontend
- 🔧 Generates backend code in any language
- 📊 Integrates with all databases
- 📝 Creates a comprehensive README.md file for the generated app
- 🗂️ Organizes the generated code into a clean project structure

## Installation

1. Clone the AppCannon repository:
   ```
   git clone https://github.com/255BITS/appcannon.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

To generate a web app using AppCannon, run the following command:

```
python appcannon.py spec_file.yaml output_directory [options]
```

- `spec_file.yaml`: The path to the YAML specification file for your app.
- `output_directory`: The directory where the generated app files will be saved.

Optional arguments:
- `-frontend`: The frontend framework to use (default: "htmx with tailwind.css").
- `-backend`: The backend framework to use (default: "flask/python3").
- `-database`: The database to use (default: "sqlite").
- `-git`: The target Git repository for the generated app.
- `-project`: The organization or project name (default: "appcannon").

## Example

Here's an example of how to use AppCannon:

```
python appcannon.py examples/todo_app.yaml generated_apps/todo_app -frontend "react" -backend "node/express" -database "mongodb"
```

This command will generate a todo app using React for the frontend, Node.js with Express for the backend, and MongoDB as the database. The generated app files will be saved in the `generated_apps/todo_app` directory.

## Changelog

* Apr 27 2024 - Initial release

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
