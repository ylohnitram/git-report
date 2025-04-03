# Git-Report

CLI tool for generating structured reports from Git commit logs.

## Installation

```bash
pip install git-report
```

## Usage

### With Local Repositories

```bash
git-report --repo /path/to/repository --since 2023-01-01 --format md --output report.md --openai-key YOUR_API_KEY
```

### With GitHub Repositories (using GitHub App)

```bash
git-report --github-repo "owner/repository" \
           --github-app-id "123456" \
           --github-private-key "/path/to/private-key.pem" \
           --github-installation-id "987654321" \
           --openai-key YOUR_API_KEY
```

You can also set these GitHub App parameters via environment variables:

```bash
export GITHUB_APP_ID="123456"
export GITHUB_PRIVATE_KEY_PATH="/path/to/private-key.pem"
export GITHUB_INSTALLATION_ID="987654321"
export OPENAI_API_KEY="your-api-key"

git-report --github-repo "owner/repository"
```

## Options

- `--repo`: Path to local Git repository
- `--github-repo`: GitHub repository (format: owner/repo)
- `--github-app-id`: GitHub App ID
- `--github-private-key`: Path to GitHub App private key file
- `--github-installation-id`: GitHub App installation ID
- `--since`: Start date (YYYY-MM-DD)
- `--until`: End date (YYYY-MM-DD)
- `--format`: Report format (md, json, html)
- `--output`: Output file
- `--openai-key`: OpenAI API key (can also be set as OPENAI_API_KEY environment variable)
