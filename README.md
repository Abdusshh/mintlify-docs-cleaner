# Documentation Migration Tool

This tool processes MDX files by removing Mintlify-specific components and cleaning up the content for other documentation tools like Docusaurus.

## Features

- Removes Mintlify-specific components
- Processes frontmatter in MDX files
- Handles nested directory structures
- Maintains file organization
- Creates backup of original files before processing

This tool was developed and tested using Upstash's documentation as an example use case for migrating from Mintlify to Docusaurus.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Abdusshh/mintlify-docs-cleaner.git
cd mintlify-docs-cleaner
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python process_docs.py
```

The script will process all MDX files in the specified directory, removing Mintlify components and preparing them for Docusaurus.

## Requirements

- Python 3.7+
- pyyaml
- python-frontmatter

## License

MIT License
