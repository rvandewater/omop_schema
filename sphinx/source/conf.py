# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "omop_schema"
copyright = "2025, Robin P. van de Water"
author = "Robin P. van de Water"
release = "0.0.4"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

import os
import sys

sys.path.insert(0, os.path.abspath(".."))  # Adjust the path to your source code

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "autoapi.extension",
]
master_doc = "index"
autoapi_type = "python"
autoapi_dirs = ["../../src/omop_schema/"]  # Adjusted path to your source code
# templates_path = ['_templates']
# html_theme = 'sphinx_rtd_theme'
