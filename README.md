# SpecGen

An AI-powered test generation tool for Python. Point it at any Python file and get a complete pytest test suite — generated, analyzed, and refined automatically.

![Python](https://img.shields.io/badge/python-3.13+-blue)
![License](https://img.shields.io/badge/license-Apache_2.0-blue)
![Anthropic](https://img.shields.io/badge/Anthropic-API-yellow)

---

## Table of Contents

- [Screenshots](#screenshots)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)

---

## Screenshots

### CodeLens Button on Functions and Classes

<img width="1280" height="696" alt="1" src="https://github.com/user-attachments/assets/d2478daa-7da7-496d-9b6c-4be4dd4104cf" />
<img width="1280" height="696" alt="2" src="https://github.com/user-attachments/assets/e7a00c7a-b67b-458c-bfeb-cc5a95ff8312" />
<img width="1280" height="696" alt="3" src="https://github.com/user-attachments/assets/05a9a06a-4b2c-4976-ac42-3fd628fcca01" />

### Output Test File

<img width="1280" height="696" alt="4" src="https://github.com/user-attachments/assets/21c928a8-20b6-4327-b482-ff947738d008" />

---

## Prerequisites

- Python 3.13+
- An Anthropic API key
- VS Code with the SpecGen extension installed

---

## Installation

### Backend

```bash
# macOS / Linux
git clone https://github.com/Ahmedmk11/spec-gen.git
cd spec-gen
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Windows (PowerShell)
git clone https://github.com/Ahmedmk11/spec-gen.git
cd spec-gen
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

### VS Code Extension

Clone the extension repo and run:

```bash
git clone https://github.com/Ahmedmk11/spec-gen-vscode.git
cd spec-gen-vscode
npm install
npm run compile
code --extensionDevelopmentPath=$(pwd)
```

---

## Configuration

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-6
```

---

## Usage

1. Start the backend server:

```bash
cd spec-gen
uv run uvicorn src.main:app --reload
```

2. Open any Python project in VS Code
3. Click the `⚡ Generate Tests` button above any function or class, or right-click a `.py` file and select **Generate Tests with SpecGen**
4. Enter the path where the test file should be saved
5. Wait for the tests to be generated and written to your project

---

## How It Works

SpecGen uses a multi-agent pipeline to produce high-quality tests:

1. **Generate** — an LLM generates a pytest test suite for the provided code
2. **Analyze** — a second LLM reviews the tests for correctness, coverage, and meaningful assertions
3. **Refine** — if the tests are lacking, a third LLM fixes the specific issues identified
4. The analyze → refine loop runs up to 3 times until the tests are accepted
