import os
import click
from git_report.git_utils import (get_commits, get_commit_diff, 
                                  get_github_commits, get_github_commit_diff)
from git_report.llm_utils import analyze_commit_with_llm
from git_report.report_gen import generate_markdown_report, generate_json_report, generate_html_report

@click.command()
@click.option('--repo', help='Path to local Git repository')
@click.option('--since', help='Start date (YYYY-MM-DD)')
@click.option('--until', help='End date (YYYY-MM-DD)')
@click.option('--format', 'report_format', type=click.Choice(['md', 'json', 'html']), 
              default='md', help='Report format')
@click.option('--output', '-o', help='Output file path')
@click.option('--openai-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--github-repo', help='GitHub repository (format: owner/repo)')
@click.option('--github-app-id', envvar='GITHUB_APP_ID', help='GitHub App ID')
@click.option('--github-private-key', envvar='GITHUB_PRIVATE_KEY_PATH', 
              help='Path to GitHub App private key file')
@click.option('--github-installation-id', envvar='GITHUB_INSTALLATION_ID', 
              help='GitHub App installation ID')
def main(repo, since, until, report_format, output, openai_key, 
         github_repo, github_app_id, github_private_key, github_installation_id):
    """Generate structured reports from Git commit logs."""
    
    # Validate input - either local repo or GitHub repo must be specified
    if not repo and not github_repo:
        click.echo("Error: Either --repo or --github-repo must be specified")
        return
    
    if repo and github_repo:
        click.echo("Error: Cannot specify both --repo and --github-repo; choose one")
        return
    
    # Determine if using local repo or GitHub
    if github_repo:
        if not github_app_id or not github_private_key or not github_installation_id:
            click.echo("Error: GitHub App ID, private key path, and installation ID are required")
            click.echo("Set these via --github-app-id, --github-private-key, --github-installation-id")
            click.echo("Or set environment variables: GITHUB_APP_ID, GITHUB_PRIVATE_KEY_PATH, GITHUB_INSTALLATION_ID")
            return
        
        click.echo(f"Analyzing commits from GitHub repository {github_repo}...")
        try:
            commits = get_github_commits(
                github_repo, 
                github_app_id, 
                github_private_key, 
                github_installation_id, 
                since_date=since, 
                until_date=until
            )
        except Exception as e:
            click.echo(f"Error accessing GitHub repository: {str(e)}")
            return
            
        click.echo(f"Found {len(commits)} commits")
        
        # Analyze commits with LLM
        analyzed_commits = []
        with click.progressbar(commits, label='Analyzing commits') as bar:
            for commit in bar:
                diff = get_github_commit_diff(commit)
                llm_analysis = analyze_commit_with_llm(commit.commit.message, diff, openai_key)
                analyzed_commits.append({
                    'sha': commit.sha,
                    'author': f"{commit.commit.author.name} <{commit.commit.author.email}>",
                    'date': commit.commit.author.date.isoformat(),
                    'message': commit.commit.message,
                    'diff': diff,
                    'llm_analysis': llm_analysis
                })
                
        # Set repo name for report
        repo_name = github_repo
    else:
        # Local repository logic
        click.echo(f"Analyzing commits from {repo}...")
        
        # Extract commit logs
        commits = get_commits(repo, since_date=since, until_date=until)
        click.echo(f"Found {len(commits)} commits")
        
        # Analyze commits with LLM
        analyzed_commits = []
        with click.progressbar(commits, label='Analyzing commits') as bar:
            for commit in bar:
                diff = get_commit_diff(commit)
                llm_analysis = analyze_commit_with_llm(commit.message, diff, openai_key)
                analyzed_commits.append({
                    'sha': commit.hexsha,
                    'author': f"{commit.author.name} <{commit.author.email}>",
                    'date': commit.committed_datetime.isoformat(),
                    'message': commit.message,
                    'diff': diff,
                    'llm_analysis': llm_analysis
                })
        
        # Set repo name for report
        repo_name = os.path.basename(repo)
    
    # Generate report
    date_range = f"{since if since else 'beginning'} to {until if until else 'end'}"
    
    if report_format == 'md':
        report = generate_markdown_report(repo_name, analyzed_commits, date_range)
    elif report_format == 'json':
        report = generate_json_report(repo_name, analyzed_commits, date_range)
    elif report_format == 'html':
        report = generate_html_report(repo_name, analyzed_commits, date_range)
    
    # Output
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(report)
        click.echo(f"Report saved to {output}")
    else:
        click.echo(report)

if __name__ == '__main__':
    main()
