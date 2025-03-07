from os import environ
from os.path import join
from typing import Dict

import requests
from dotenv import load_dotenv
from markdown import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension

load_dotenv()

def escape_markdown_content(md_content: str) -> str:
    escape_mappings = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    }
    for char, escape_sequence in escape_mappings.items():
        md_content = md_content.replace(char, escape_sequence)
    return md_content


workspace = environ.get('GITHUB_WORKSPACE')
if not workspace:
    print('No workspace is set')
    exit(1)

envs: Dict[str, str] = {}
for key in ['from', 'to', 'cloud', 'user', 'token']:
    value = environ.get(f'INPUT_{key.upper()}')
    if not value:
        print(f'Missing value for {key}')
        exit(1)
    envs[key] = value

with open(join(workspace, envs['from'])) as f:
    md = f.read()

url = f"https://{envs['cloud']}.atlassian.net/wiki/rest/api/content/{envs['to']}"

current = requests.get(url, auth=(envs['user'], envs['token'])).json()

# Escape the markdown content before converting it
escaped_md = escape_markdown_content(md)

html = markdown(escaped_md, extensions=[GithubFlavoredMarkdownExtension()])

content = {
    'id': current['id'],
    'type': current['type'],
    'title': current['title'],
    'version': {'number': current['version']['number'] + 1},
    'body': {
        'editor': {
            'value': html,
            'representation': 'editor'
        }
    }
}

updated = requests.put(url, json=content, auth=(
    envs['user'], envs['token']))
print('Status Code:', updated.status_code)
print('Response Body:', updated.text)

