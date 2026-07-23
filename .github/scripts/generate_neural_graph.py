import os
import requests
import json
from datetime import datetime

USERNAME = os.environ.get('USERNAME')
TOKEN = os.environ.get('GITHUB_TOKEN')

def fetch_contribution_data():
    headers = {'Authorization': f'bearer {TOKEN}'}
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query, 'variables': {'userName': USERNAME}},
        headers=headers
    )
    if response.status_code == 200:
        return response.json()['data']['user']['contributionsCollection']['contributionCalendar']
    return None

def generate_svg(calendar):
    weeks = calendar['weeks']
    
    # SVG Configuration
    svg_width = 800
    svg_height = 150
    padding_x = 20
    padding_y = 20
    
    # Calculate spacing
    cols = len(weeks)
    rows = 7
    cell_w = (svg_width - 2 * padding_x) / cols
    cell_h = (svg_height - 2 * padding_y) / rows
    
    # SVG start
    svg = [
        f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">',
        '      <feGaussianBlur stdDeviation="2" result="blur" />',
        '      <feComposite in="SourceGraphic" in2="blur" operator="over" />',
        '    </filter>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#0d1117" rx="6" />', # Dark background
    ]
    
    # Collect nodes for drawing connections
    active_nodes = []
    
    for i, week in enumerate(weeks):
        for j, day in enumerate(week['contributionDays']):
            count = day['contributionCount']
            x = padding_x + i * cell_w
            y = padding_y + j * cell_h
            
            if count > 0:
                # Intensity scale (cap at 10)
                intensity = min(count / 10.0, 1.0)
                radius = 1.5 + (intensity * 2.5) # Dynamic sizing
                opacity = 0.3 + (intensity * 0.7)
                active_nodes.append((x, y, intensity))
                
                # Draw Node
                svg.append(f'  <circle cx="{x}" cy="{y}" r="{radius}" fill="#58a6ff" opacity="{opacity}" filter="url(#glow)"/>')
            else:
                # Draw subtle background node
                svg.append(f'  <circle cx="{x}" cy="{y}" r="1" fill="#30363d" opacity="0.3"/>')
                
    # Draw faint neural connections between nearby active nodes
    for i in range(len(active_nodes)):
        x1, y1, int1 = active_nodes[i]
        # Only connect a fraction to avoid clutter
        if i % 3 != 0: continue 
        for j in range(i+1, min(i+10, len(active_nodes))):
            x2, y2, int2 = active_nodes[j]
            dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            if dist < 40: # Proximity threshold
                line_opacity = (int1 + int2) * 0.15 # Very subtle line
                svg.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#58a6ff" stroke-width="0.5" opacity="{line_opacity}" />')

    # Add terminal-like text summary
    total = calendar['totalContributions']
    svg.append(f'  <text x="20" y="{svg_height - 5}" font-family="monospace" font-size="10" fill="#8b949e">> SYSTEM_LOG: {total} neural activations in the last 365 days.</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)

if __name__ == '__main__':
    data = fetch_contribution_data()
    if data:
        svg_content = generate_svg(data)
        os.makedirs('assets', exist_ok=True)
        with open('assets/neural_graph.svg', 'w') as f:
            f.write(svg_content)
