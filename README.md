# UMLOpenAIPlugin 

> **Join the [ChatGPT plugins waitlist here](https://openai.com/waitlist/plugins)!**

UMLOpenAIPlugin is a plugin for ChatGPT that allows users to generate diagrams using PlantUML or Mermaid based on their preferences. This plugin enhances ChatGPT's capabilities by providing users with a seamless way to create diverse and creative output options in the form of diagrams.

## Features
- Generate diagrams using PlantUML or Mermaid
- Seamlessly integrates with ChatGPT
- User-friendly interface for requesting diagrams
- Enhances ChatGPT's capabilities with diverse output options

## Installation
Before using the plugin, make sure to have the following prerequisites installed:

- Python 3.6+
- FastAPI
- PlantUML
- Mermaid
- uvicorn

1. Install Python 3.10, if not already installed.
2. Clone the repository: `git clone https://github.com/openai/chatgpt-retrieval-plugin.git`
3. Navigate to the cloned repository directory: `cd /path/to/chatgpt-retrieval-plugin`
4. Install poetry: `pip install poetry`
5. Create a new virtual environment with Python 3.10: `poetry env use python3.10`
6. Activate the virtual environment: `poetry shell`
7. Install app dependencies: `poetry install`
8. Create a [bearer token](#general-environment-variables)
9. Set the required environment variables:

## Setup

To install the required packages for this plugin, run the following command:

```bash
pip install -r requirements.txt
```

To run the plugin, enter the following command:

```bash
python main.py
```

Once the local server is running:

```bash
uvicorn main:app --host 127.0.0.1 --port 5003
```

1. Navigate to https://chat.openai.com. 
2. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter in `localhost:5003` since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start with a question like "What is on my todo list" and then try adding something to it as well! 


### Testing in ChatGPT

To test a locally hosted plugin in ChatGPT, follow these steps:

1. Run the API on localhost: `poetry run dev`
2. Follow the instructions in the [Testing a Localhost Plugin in ChatGPT](#testing-a-localhost-plugin-in-chatgpt) section of the README.

For more detailed information on setting up, developing, and deploying the ChatGPT Retrieval Plugin, refer to the full Development section below.

## Getting help

If you run into issues or have questions building a plugin, please join our [Developer community forum](https://community.openai.com/c/chat-plugins/20).
