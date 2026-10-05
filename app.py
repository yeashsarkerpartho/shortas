import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

req_session = requests.Session()

def fetch_dynamic_token(base_domain, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8'
    }
    try:
        response = session.get(base_domain + '/', headers=headers, verify=False, timeout=10)
        html = response.text
        token = ""
        
        next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
        if next_data_match:
            token_match = re.search(r'"token"\s*:\s*"([a-zA-Z0-9\.\-_]+)"', next_data_match.group(1), re.IGNORECASE)
            if token_match:
                token = token_match.group(1)
        
        if not token:
            fallback_match = re.search(r'"(?:accessToken|jwtToken|token)"\s*:\s*"([a-zA-Z0-9\.\-_]{20,})"', html, re.IGNORECASE)
            if fallback_match:
                token = fallback_match.group(1)
                
        return token
    except:
        return ""

config = {
    'base_domain': 'https://themoviebox.xyz',
    'ranking_path': '/ranking-list/eL6uk3fbsY4?id=4175575772020854200&page_from=more_SUBJECTS_MOVIE',
    'output_file': 'scraped_data_output2.json',
    'cache_items': 'ranking_items_cache2.json',
    'category_name': 'Bengali Collection',
    'delay_between_episodes_ms': 120,
    'cooldown_seconds': 2,
    'jwt_token': ''
}

config['ranking_url'] = config['base_domain'] + config['ranking_path']
config['detail_api'] = config['base_domain'] + '/wefeed-h5api-bff/subject/detail'
config['play_api'] = config['base_domain'] + '/wefeed-h5api-bff/subject/play'

if not config['jwt_token']:
    config['jwt_token'] = fetch_dynamic_token(config['base_domain'], req_session)
