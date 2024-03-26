from pallets_sphinx_themes import ProjectLink, get_version

# Project --------------------------------------------------------------

project = "Cally"
copyright = "2024 Leon Wright"
author = "Leon Wright"
release, version = get_version("cally")

# General --------------------------------------------------------------

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.log_cabinet",
    "pallets_sphinx_themes",
    "sphinx_issues",
    "sphinx_tabs.tabs",
]
autodoc_typehints = "description"
intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}
issues_github_path = "CallyCo-io/Cally"

# HTML -----------------------------------------------------------------
html_theme = "click"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("PyPI Releases", "https://pypi.org/project/cally/"),
        ProjectLink("Source Code", "https://github.com/CallyCo-io/Cally/"),
        ProjectLink("Issue Tracker", "https://github.com/CallyCo-io/Cally/issues/"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html", "ethicalads.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html", "ethicalads.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html", "ethicalads.html"]}
html_static_path = ["_static"]
html_title = f"Cally Documentation ({version})"
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [(master_doc, f"Cally-{version}.tex", html_title, author, "manual")]
