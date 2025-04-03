import os
import click
from git_report.git_utils import get_commits, get_commit_diff
from git_report.llm_utils import analyze_commit_with_llm
from git_report.report_gen import generate_markdown_report, generate_json_report, generate_html_report

@click.command()
@click.option('--repo', required=True, help='Path to Git repository')
@click.option('--since', help='Start date (YYYY-MM-DD)')
@click.option('--until', help='End date (YYYY-MM-DD)')
@click.option('--format', 'report_format', type=click.Choice(['md', 'json', 'html']), 
              default='md', help='Report format')
@click.option('--output', '-o', help='Output file path')
@click.option('--openai-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
def main(repo, since, until, report_format, output, openai_key):
    """Generate structured reports from Git commit logs."""
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
    
    # Generate report
    repo_name = os.path.basename(repo)
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
