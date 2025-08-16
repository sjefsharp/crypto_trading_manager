#!/usr/bin/env python3
"""
Bulk fix typing issues in the codebase
"""
import os
import re
from pathlib import Path

def fix_file_typing(file_path: str):
    """Fix common typing issues in a file"""
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # Fix Dict without type params
    content = re.sub(r'\bDict\b(?!\[)', 'Dict[str, Any]', content)

    # Fix List without type params
    content = re.sub(r'\bList\b(?!\[)', 'List[Any]', content)

    # Fix list without type params in return annotations
    content = re.sub(r'-> list\b', '-> List[Any]', content)

    # Fix dict without type params in return annotations
    content = re.sub(r'-> dict\b', '-> Dict[str, Any]', content)

    # Add missing -> None for functions that don't return anything
    patterns = [
        (r'(def \w+\([^)]*\)):\s*\n(\s*"""[^"]*"""\s*\n)?(\s*(?:if|for|while|try|with))', r'\1 -> None:\n\2\3'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Add Any import if needed
    if 'Any' in content and 'from typing import' in content and 'Any' not in content.split('from typing import')[1].split('\n')[0]:
        content = re.sub(r'from typing import ([^\n]+)', r'from typing import \1, Any', content)

    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed typing in {file_path}")

def main():
    """Fix typing in all Python files"""
    backend_dir = Path(__file__).parent.parent / 'backend'

    for py_file in backend_dir.rglob('*.py'):
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue
        fix_file_typing(str(py_file))

if __name__ == '__main__':
    main()
