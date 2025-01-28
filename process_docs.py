import os
import re
from pathlib import Path
import shutil
import logging
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocsMigrator:
    def __init__(self, docs_dir):
        self.docs_dir = Path(docs_dir)
        self.backup_dir = self.docs_dir.parent / 'docs_backup'
        
        # Mintlify-specific components that need to be commented out or transformed
        self.mintlify_components = {
            'Frame': 'img wrapper',
            'Card': 'custom card component',
            'CardGroup': 'card group component',
            'CodeGroup': 'code group wrapper',
            'ParamField': 'parameter field component',
            'Accordion': 'accordion component',
            'AccordionGroup': 'accordion group component',
            'Steps': 'steps component',
            'Tabs': 'tabs component',
            'Tab': 'tab component',
            'ResponseField': 'response field component',
            'RequestExample': 'request example component',
            'ResponseExample': 'response example component',
            'Tip': 'tip component',
            'Info': 'info component',
            'Warning': 'warning component',
            'Note': 'note component',
        }

        # Mapping of Mintlify frontmatter fields to Docusaurus
        self.frontmatter_mapping = {
            'sidebarTitle': 'sidebar_label',
            'description': 'description',
            'title': 'title',
        }
        
    def create_backup(self):
        """Create a backup of the docs directory"""
        if not self.backup_dir.exists():
            shutil.copytree(self.docs_dir, self.backup_dir)
            logging.info(f'Created backup at {self.backup_dir}')

    def is_binary_file(self, file_path):
        """Check if file is binary"""
        try:
            with open(file_path, 'tr') as check_file:
                check_file.read()
                return False
        except UnicodeDecodeError:
            return True

    def process_mdx_content(self, content):
        # First remove nested components
        components = ['Card', 'CardGroup', 'Tabs', 'TabItem', 'ResponseField', 'ParamField', 
                     'Expandable', 'RequestExample', 'ResponseExample', 'CodeGroup', 'Tip', 'Info', 'Warning', 
                     'Note', 'Steps', 'Step', 'Frame', 'Check', 'CodeBlock', 'Col', 'TagFilters'
                     'Properties', 'Property', 'Accordion', 'AccordionGroup', 'Update', 'Snippet']
        
        # Remove all Mintlify comment blocks
        content = re.sub(r'\{/\*\s*Mintlify.*?\*/\}', '', content, flags=re.DOTALL)
        
        # Remove nested components first
        for component in components:
            pattern = f'<{component}[^>]*>.*?</{component}>'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Remove self-closing components
        for component in components:
            pattern = f'<{component}[^>]*/>'
            content = re.sub(pattern, '', content)
        
        # Remove any remaining component tags
        for component in components:
            content = re.sub(f'<{component}[^>]*>', '', content)
            content = re.sub(f'</{component}>', '', content)
        
        # Clean up multiple blank lines and whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s+\n', '\n', content)
        
        return content.strip()

    def clean_frontmatter(self, content):
        """Clean and transform frontmatter to Docusaurus format"""
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return content

        try:
            # Parse the existing frontmatter
            fm_content = frontmatter_match.group(1)
            fm_data = yaml.safe_load(fm_content) or {}

            # Create new frontmatter with mapped fields and no duplicates
            new_fm = {}
            
            # Handle title first
            if 'title' in fm_data:
                value = fm_data['title'].strip('"\'')  # Remove any existing quotes
                new_fm['title'] = f'"{value}"'  # Add single set of quotes
            
            # Map and clean other fields
            for old_key, new_key in self.frontmatter_mapping.items():
                if old_key in fm_data and old_key != 'title':  # Skip title as we handled it
                    value = fm_data[old_key]
                    if isinstance(value, str):
                        value = value.strip('"\'')  # Remove any existing quotes
                        value = f'"{value}"'  # Add single set of quotes
                    new_fm[new_key] = value

            # Generate new frontmatter YAML with block style
            new_fm_str = yaml.dump(new_fm, default_flow_style=False, allow_unicode=True)
            
            # Replace old frontmatter with new
            return f'---\n{new_fm_str}---\n' + content[len(frontmatter_match.group(0)):]

        except yaml.YAMLError as e:
            logging.error(f'Error parsing frontmatter: {e}')
            return content

    def clean_file(self, file_path):
        """Clean a single file"""
        if self.is_binary_file(file_path):
            logging.info(f'Skipping binary file: {file_path}')
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Only process .mdx and .md files
            if file_path.suffix.lower() not in ['.md', '.mdx']:
                return

            # Transform the content
            content = self.clean_frontmatter(content)
            content = self.process_mdx_content(content)

            # Write back the transformed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logging.info(f'Transformed file: {file_path}')

        except Exception as e:
            logging.error(f'Error processing {file_path}: {str(e)}')

    def process_directory(self):
        """Process all files in the docs directory"""
        # Create backup first
        self.create_backup()

        # Process all files
        for file_path in self.docs_dir.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                self.clean_file(file_path)

def main():
    docs_dir = Path('/Users/abdullahenesgules/Upstash/Projects/process-docs/docs')
    if not docs_dir.exists():
        logging.error(f'Docs directory not found: {docs_dir}')
        return

    migrator = DocsMigrator(docs_dir)
    migrator.process_directory()
    logging.info('Documentation migration completed!')

if __name__ == '__main__':
    main()
