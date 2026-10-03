"""
LinkedIn Post Scheduler via Buffer API
"""

import os
import sys
import re
import json
import zipfile
import xml.etree.ElementTree as ET
import urllib.request
import ssl
import argparse
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

def load_env(env_path=None):
    if env_path is None:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

def extract_posts_from_docx(docx_path):
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"File not found: {docx_path}")
        
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read("word/document.xml")
    
    tree = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    paragraphs = []
    for p in tree.iterfind('.//w:p', namespaces):
        texts = [node.text for node in p.iterfind('.//w:t', namespaces) if node.text]
        paragraphs.append("".join(texts))
    
    posts = []
    current_header = None
    current_lines = []
    
    for line in paragraphs:
        m = re.match(r"^Post\s+(\d+)", line.strip(), re.IGNORECASE)
        if m:
            if current_header is not None:
                body = "\n".join(current_lines).strip()
                body = re.sub(r'[\r\n]*─+[\r\n]*', '', body).strip()
                posts.append((current_header, body))
            current_header = f"Post {m.group(1)}"
            current_lines = []
        else:
            current_lines.append(line)
            
    if current_header is not None:
        body = "\n".join(current_lines).strip()
        body = re.sub(r'[\r\n]*─+[\r\n]*', '', body).strip()
        posts.append((current_header, body))
        
    return posts

def call_buffer_graphql(api_key, query, variables=None):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
        
    ctx = ssl.create_default_context()
    req = urllib.request.Request('https://api.buffer.com', data=json.dumps(payload).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req, context=ctx) as response:
        return json.loads(response.read().decode('utf-8'))

def schedule_post(api_key, channel_id, text, due_at_iso):
    mutation = '''
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post {
            id
            dueAt
          }
        }
        ... on LimitReachedError {
          message
        }
        ... on InvalidInputError {
          message
        }
        ... on UnexpectedError {
          message
        }
        ... on UnauthorizedError {
          message
        }
      }
    }
    '''
    variables = {
        'input': {
            'channelId': channel_id,
            'mode': 'customScheduled',
            'schedulingType': 'automatic',
            'needsApproval': False,
            'dueAt': due_at_iso,
            'text': text
        }
    }
    return call_buffer_graphql(api_key, mutation, variables)

def main():
    parser = argparse.ArgumentParser(description="Schedule LinkedIn posts via Buffer API")
    parser.add_argument('--file', default=r"c:\Users\Iba Zaidi\Desktop\LinkedIn-Analytics-Posts\LinkedIn_Data_Analytics_Top_30_Posts.docx")
    parser.add_argument('--start-post', type=int, default=1, help="Starting post number (1-indexed)")
    parser.add_argument('--count', type=int, default=10, help="Number of posts to schedule")
    parser.add_argument('--start-date', type=str, default="2026-10-04", help="Start date in YYYY-MM-DD format")
    parser.add_argument('--time', type=str, default="09:30", help="Posting time in HH:MM (local time)")
    parser.add_argument('--tz-offset', type=float, default=5.5, help="Timezone offset from UTC in hours (default: 5.5 for IST)")
    args = parser.parse_args()

    env = load_env()
    api_key = os.environ.get('BUFFER_API_KEY') or env.get('BUFFER_API_KEY')
    channel_id = os.environ.get('BUFFER_LINKEDIN_CHANNEL_ID') or env.get('BUFFER_LINKEDIN_CHANNEL_ID')

    if not api_key or not channel_id:
        print("Error: Missing BUFFER_API_KEY or BUFFER_LINKEDIN_CHANNEL_ID.")
        sys.exit(1)

    posts = extract_posts_from_docx(args.file)
    print(f"Total posts found in document: {len(posts)}")

    start_idx = args.start_post - 1
    end_idx = min(start_idx + args.count, len(posts))
    posts_to_schedule = posts[start_idx:end_idx]

    hr, mn = map(int, args.time.split(':'))
    base_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(hour=hr, minute=mn, second=0)

    print(f"Scheduling {len(posts_to_schedule)} posts starting from Post {args.start_post} on {args.start_date} at {args.time} IST...\n")

    for i, (header, text) in enumerate(posts_to_schedule):
        post_local_dt = base_date + timedelta(days=i)
        post_utc_dt = post_local_dt - timedelta(hours=args.tz_offset)
        due_at_iso = post_utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        local_display = post_local_dt.strftime("%A, %b %d, %Y at %I:%M %p IST")

        print(f"[{i+1}/{len(posts_to_schedule)}] Scheduling {header} for {local_display}...")
        res = schedule_post(api_key, channel_id, text, due_at_iso)
        data = res.get('data', {}).get('createPost', {})

        if 'post' in data:
            print(f"   --> SUCCESS! Post ID: {data['post']['id']}")
        else:
            print(f"   --> FAILED: {data}")

if __name__ == '__main__':
    main()
