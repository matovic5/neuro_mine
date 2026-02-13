# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'neuro_mine'
copyright = '2026, Danica Matovic, Martin Haesemeyer'
author = 'Danica Matovic, Martin Haesemeyer'
release = '0.8.2'

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- HTML output -------------------------------------------------

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_theme_options = {
    "github_url": "https://github.com/matovic5/neuro_mine",
    "use_edit_page_button": True,
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
}
