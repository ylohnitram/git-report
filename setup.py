from setuptools import setup, find_packages

setup(
    name="git-report",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "GitPython>=3.1.0",
        "click>=8.0.0",
        "openai>=1.0.0",
        "markdown>=3.3.0",
        "jinja2>=3.0.0",
        "PyGithub>=1.55",  # For GitHub API
        "PyJWT>=2.0.0",  # For GitHub App JWT
        "cryptography>=3.4.0",  # For GitHub App private key handling
    ],
    entry_points={
        "console_scripts": [
            "git-report=git_report.cli:main",
        ],
    },
    python_requires=">=3.8",
    description="CLI tool for generating structured reports from Git commit logs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
