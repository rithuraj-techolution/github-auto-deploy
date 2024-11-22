
"""
This module maps the main functions of different language-specific modules to their respective language names.
"""

# Importing main functions from different language-specific modules
from Languages.Csharp import main_function as csharp_main_function
from Languages.Python import main_function as python_main_function
from Languages.Javascript import main_function as js_main_function
from Languages.Typescript import main_function as ts_main_function
from Languages.document import main_function as document_main_function




project_mapping = {
    "csharp": csharp_main_function,
    "python": python_main_function,
    "javascript": js_main_function,
    "typescript" :ts_main_function,
    "document":  document_main_function
}
