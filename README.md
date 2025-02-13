# Cookidoo Agent

Cookidoo Agent is a sophisticated Python application that integrates the OpenAI API, Milvus vector database, and the Cookidoo API to fetch, process, and search for recipes based on natural language queries. This project is designed with modern Python best practices including asynchronous programming, modular architecture, and type hinting to deliver an impressive and efficient solution.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Querying Recipes](#querying-recipes)
  - [Loading Recipes into Milvus](#loading-recipes-into-milvus)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

Cookidoo Agent allows you to:
- **Fetch** recipes asynchronously from the Cookidoo API.
- **Process** recipes by generating condensed text representations.
- **Compute embeddings** for these representations using OpenAI’s `text-embedding-3-small` model.
- **Store and index** recipes in a Milvus vector database.
- **Search** recipes via vector similarity and generate human-readable responses using OpenAI ChatGPT.

This application is ideal for demonstrating advanced Python programming, asynchronous I/O, and integration of multiple external APIs and services.

## Features

- **Asynchronous Operations:** Utilizes `asyncio` and `aiohttp` for efficient network operations.
- **Advanced API Integrations:** Leverages OpenAI for both text embeddings and chat-based completions.
- **Vector Search:** Uses Milvus for fast, scalable similarity searches on recipe embeddings.
- **Modular Codebase:** Clear separation of concerns with well-structured packages and modules.
- **Comprehensive Logging & Error Handling:** Centralized configuration ensures clear diagnostics.

## Project Structure

```plaintext
cookidoo_agent/
├── __init__.py
├── config.py               # Central configuration (logging, env variables, API keys)
├── main.py                 # Entry point for CLI commands (query & load)
├── load_database.py        # Module for fetching and loading recipes into Milvus
├── query_recipe.py         # Module for processing queries and generating responses
├── utils.py                # Utility functions (e.g., embedding generation)
└── cookidoo/
    ├── __init__.py         # Cookidoo API integration
    ├── helpers.py          # Helper functions for localization
    └── types.py            # Domain models & dataclasses for recipe data
.env
.gitignore
requirements.txt
README.md
```

## Prerequisites

- Python 3.8+ (recommended)
- A running Milvus instance (configured with host/port as specified in the .env)
- A valid OpenAI API key
- Internet connectivity (to access external APIs)

## Installation

1. Clone the repository
```bash
git clone https://github.com/karolk75/cookidoo-agent.git
cd cookidoo_agent
```

2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Configure Environment Variables
Create a .env file (use .example.env) in the project root with the following content:
```bash
OPENAI_API_KEY=
MILVUS_HOST=
MILVUS_PORT=
```

## Configuration

All configuration is centralized in cookidoo_agent/config.py:

- OpenAI API Key: Loaded from the .env file.
- Milvus Connection: Host and port are configurable via environment variables.
- Logging: Configured to provide timestamped output with a consistent format.

Modify these settings as needed to match your environment.

## Usage

The project provides two main functionalities:

#### Loading Recipes into Milvus
Load recipes from the Cookidoo API into the Milvus vector database. This command fetches recipes in batches, processes them, computes embeddings, and stores them.

Run the load command with:

```bash
python -m cookidoo_agent.main --command load
```
**Note**: This is fetching only Polish recipies. Adjust **cookidoo.__init__.py** file if needed

#### Querying Recipes
Query recipes by providing a natural language query. This will:

- Extract key search criteria using ChatGPT.
- Compute embeddings for the refined query.
- Search the Milvus database for similar recipes.
- Generate a human-readable answer with ChatGPT.
- Run the query command as follows:

```bash
python -m cookidoo_agent.main --command query --query "Wyszukaj mi trzy przepisy na obiad, w których składniki są podobne (żeby kupić jak najmniej rzeczy)"
```
If you omit the --query argument, a test query is executed.

## Contributing
Contributions are welcome! If you have ideas, bug fixes, or enhancements, please open an issue or submit a pull request. Follow the existing code style and documentation practices.

