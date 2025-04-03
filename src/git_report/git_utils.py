from git import Repo
import jwt
import time
import requests
from github import Github
from datetime import datetime

def get_commits(repo_path, since_date=None, until_date=None, author=None, branch='main'):
    """Extract commits from repository with optional filtering"""
    repo = Repo(repo_path)
    
    # Build git log command with filters
    kwargs = {}
    if since_date:
        kwargs['since'] = since_date
    if until_date:
        kwargs['until'] = until_date
    
    # Get commits
    if author:
        commits = list(repo.iter_commits(branch, author=author, **kwargs))
    else:
        commits = list(repo.iter_commits(branch, **kwargs))
        
    return commits

def get_commit_diff(commit):
    """Get diff for a given commit"""
    if not commit.parents:  # Initial commit
        return commit.diff(None, create_patch=True)
    
    diffs = commit.parents[0].diff(commit, create_patch=True)
    diff_text = ""
    
    for diff_item in diffs:
        if diff_item.diff:
            diff_text += diff_item.diff.decode('utf-8', errors='replace') + "\n"
    
    return diff_text

def create_github_app_jwt(app_id, private_key_path):
    """Create a JWT for GitHub App authentication"""
    # Read the private key
    with open(private_key_path, 'r') as key_file:
        private_key = key_file.read()
    
    # Create JWT
    now = int(time.time())
    payload = {
        'iat': now,               # Issued at time
        'exp': now + (10 * 60),   # JWT expiration time (10 minutes)
        'iss': app_id             # GitHub App's identifier
    }
    
    encoded_jwt = jwt.encode(
        payload,
        private_key,
        algorithm='RS256'
    )
    
    return encoded_jwt

def get_installation_token(app_id, private_key_path, installation_id):
    """Get an installation access token for a GitHub App installation"""
    jwt_token = create_github_app_jwt(app_id, private_key_path)
    
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code != 201:
        raise Exception(f"Failed to get installation token: {response.json()}")
    
    return response.json()["token"]

def get_github_commits(repo_name, app_id, private_key_path, installation_id, since_date=None, until_date=None):
    """Extract commits from GitHub repository with optional filtering using GitHub App auth"""
    # Get installation token
    token = get_installation_token(app_id, private_key_path, installation_id)
    
    # Use token with PyGithub
    g = Github(token)
    repo = g.get_repo(repo_name)
    
    # Prepare date filters
    kwargs = {}
    if since_date:
        since_datetime = datetime.strptime(since_date, "%Y-%m-%d")
        kwargs['since'] = since_datetime
    if until_date:
        until_datetime = datetime.strptime(until_date, "%Y-%m-%d")
        kwargs['until'] = until_datetime
    
    # Get commits
    commits = list(repo.get_commits(**kwargs))
    
    return commits

def get_github_commit_diff(commit):
    """Get diff for a GitHub commit"""
    # GitHub API doesn't directly provide full diffs, so we extract information from files
    files_changed = commit.files
    diff_text = ""
    
    for file in files_changed:
        diff_text += f"File: {file.filename}\n"
        diff_text += f"Status: {file.status}\n"
        diff_text += f"Changes: +{file.additions} -{file.deletions}\n"
        if file.patch:
            diff_text += f"Patch:\n{file.patch}\n"
        diff_text += "\n"
    
    return diff_text
