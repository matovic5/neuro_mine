# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'NeuroMINE'
copyright = '2026, Danica Matovic, Martin Haesemeyer'
author = 'Danica Matovic, Martin Haesemeyer'
release = '1.0.1'

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_rtd_theme"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
}

html_static_path = ['_static']

html_context = {
    "github_user": "matovic5",
    "github_repo": "neuro_mine",
    "github_version": "main",
    "doc_path": "docs",
}

