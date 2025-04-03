from git import Repo

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
