import os
import requests
from datetime import datetime

USERNAME = os.environ.get('USERNAME')
TOKEN = os.environ.get('GITHUB_TOKEN')

def get_latest_commit():
    headers = {'Authorization': f'token {TOKEN}'} if TOKEN else {}
    response = requests.get(f'https://api.github.com/users/{USERNAME}/events/public', headers=headers)
    
    if response.status_code != 200:
        return None
        
    for event in response.json():
        if event['type'] == 'PushEvent' and event['payload']['commits']:
            repo_name = event['repo']['name']
            latest_commit = event['payload']['commits'][-1]['message'].split('\n')[0]
            created_at = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            
            diff = datetime.utcnow() - created_at
            hours = int(diff.total_seconds() // 3600)
            time_str = "just now" if hours == 0 else (f"{hours}h ago" if hours < 24 else f"{hours // 24}d ago")
                
            return f"> ⚡ Latest Commit: [{repo_name}](https://github.com/{repo_name}) - \"{latest_commit}\" ({time_str})"
    return None

def update_readme(commit_text):
    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()
        
    start_marker = "<!-- LATEST_COMMIT_START -->"
    end_marker = "<!-- LATEST_COMMIT_END -->"
    
    if start_marker in readme and end_marker in readme:
        start_idx = readme.find(start_marker) + len(start_marker)
        end_idx = readme.find(end_marker)
        
        new_readme = readme[:start_idx] + "\n" + commit_text + "\n" + readme[end_idx:]
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_readme)

if __name__ == '__main__':
    commit_text = get_latest_commit()
    if commit_text:
        update_readme(commit_text)
