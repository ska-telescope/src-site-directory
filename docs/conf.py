import os
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ska-src-site-capabilities-api'
copyright = '2024, Rob Barnsley'
author = 'Rob Barnsley'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinxcontrib.mermaid', 'myst_parser', 'autoapi.extension']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for MD ----------------------------------------------------------
source_suffix = ['.rst', '.md']

# -- Options for apidoc ------------------------------------------------------
autoapi_dirs = '../src/ska_src_site_capabilities_api'
autoapi_member_order = 'alphabetical'

# -- Options for Mermaid -----------------------------------------------------
# https://pypi.org/project/sphinxcontrib-mermaid/
mermaid_init_js = '''mermaid.initialize({
      startOnLoad:true,
      "theme": "default",
      "sequence": {
        "noteAlign": "left",
        "noteFontFamily": "verdana",
        "showSequenceNumbers": true,
        "noteMargin": 20,
        "rightAngles": true
      }
    });'''