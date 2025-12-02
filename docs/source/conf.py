import os
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Recipe Search Engine"
copyright = "2025, Iliès SGHIAR"
author = "Iliès SGHIAR"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


sys.path.insert(0, os.path.abspath("../src"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "myst_parser",
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_baseurl = "https://ilies-sghiar.github.io/RecipeSearchEngine/"
html_theme = "pydata_sphinx_theme"
html_title = "Recipe Search Engine"
html_logo = "menu.png"
html_static_path = ["_static"]

html_theme_options = {
    "logo": {
        "image_light": "menu.png",
        "image_dark": "menu.png",
        "text": "Recipe Search Engine",
    }
}
