# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

from bibtutils import __version__  # noqa: E402

# -- Project information -----------------------------------------------------

project = "bibtutils"
copyright = "2021, Matthew OBrien"
author = "Matthew OBrien"
version = __version__
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

autosummary_generate = True

autodoc_mock_imports = ["google", "dateutil", "requests"]

coverage_show_missing_items = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# https://alabaster.readthedocs.io/en/latest/customization.html
html_theme = "alabaster"
html_theme_options = {
    "page_width": "90%",
    "logo": "./bibt.ico",
    "logo_name": True,
    "logo_text_align": "center",
    "touch_icon": "./bibt.ico",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom.css"]
# html_style = 'custom.css'

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True


intersphinx_mapping = {
    "python": ("https://python.readthedocs.org/en/latest/", None),
    "gcp_storage": ("https://googleapis.dev/python/storage/latest/", None),
    "gcp_bigquery": ("https://googleapis.dev/python/bigquery/latest/", None),
    "google_auth": ("https://googleapis.dev/python/google-auth/latest/", None),
}
