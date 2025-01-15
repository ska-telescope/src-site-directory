import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))
sys.path.insert(1, os.path.abspath("../.."))
sys.path.insert(2, os.path.abspath("../../tests"))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ska-src-site-capabilities-api'
copyright = '2024, Rob Barnsley'
author = 'Rob Barnsley'

# The short X.Y version
version = "1.0"
# The full version, including alpha/beta/rc tags
release = "1.0"

autodoc_typehints = "none"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinxcontrib.mermaid', 'sphinxcontrib.plantuml', 'myst_parser', 'autoapi.extension', "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "m2r2",
]
autodoc_typehints = "none"

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_typehints = "none"

# The master toctree document.
master_doc = "index"
 
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'ska_ser_sphinx_theme'
# html_static_path = ['_static']
# html_css_files = [
#     'css/custom.css',
# ]
html_context = {}
exclude_patterns = []


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "SKASRCSiteCapabilitiesAPIdoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "SKASRCSiteCapabilitiesAPIdoc.tex", "SKASRCSiteCapabilitiesAPIdoc Documentation", "manual"),
]

# -- Options for MD ----------------------------------------------------------
source_suffix = ['.rst', '.md']

# -- Options for apidoc ------------------------------------------------------
autoapi_dirs = '../../src/ska_src_site_capabilities_api'
autoapi_member_order = 'alphabetical'
autoapi_options = ['members', 'undoc-members', 'private-members', 'show-inheritance', 
        'show-inheritance-diagram', 'show-module-summary', 'special-members', 'imported-members']

# -- Options for plantuml ----------------------------------------------------
plantuml = '/usr/bin/plantuml'

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
