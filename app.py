import os
import re
import json
import time
import urllib.parse
from flask import Flask, request, Response, jsonify
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

CONFIG = {
    'base_domain': 'https://themoviebox.xyz',
    'ranking_path': '/ranking-list/eL6uk3fbsY4?id=4175575772020854200&page_from=more_SUBJECTS_MOVIE',
    'output_file': os.path.join(os.path.dirname(__file__), 'sshortas_sars.json'),
    'category_name': 'Bengali Collection',
    'delay_between_episodes_ms': 120,
    'cooldown_seconds': 2,
    'jwt_token': ''
}

CONFIG['ranking_url'] = CONFIG['base_domain'] + CONFIG['ranking_path']
CONFIG['detail_api'] = CONFIG['base_domain'] + '/wefeed-h5api-bff/subject/detail'
CONFIG['play_api'] = CONFIG['base_domain'] + '/wefeed-h5api-bff/subject/play'

TARGET_CONTENT_LIST = [
    'detail/mahabharat-hindi-qV4oETYbuc2?id=1847636170218291288&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/where-is-home-bengali-6XoMSqzVHc1?id=1011335773633364112&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/little-poor-thing-rises-by-bearing-children-reigns-over-the-electronics-factory-bengali-8wiolm5dap?id=340656650174512800&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/daughter-of-the-secret-tycoon-bengali-SNzLElsh1J2?id=2288047444120209032&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/the-mysterious-master-chef-bengali-UgsCDuzFps6?id=5420439523421570376&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/dragon-traveling-the-world-bengali-w29TKIrCWTa?id=9150332540815917096&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/lucifer-my-boyfriend-from-hell-bengali-GHdITaqEbOa?id=9072392078532953112&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/immortal-cultivation-frenzy-starting-with-divorce-bengali-ggcwE31icR8?id=7434544044375981696&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/cubicles-cupid-twist-bengali-wOxYdNaWKW4?id=4152596994760098832&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/becoming-light-bengali-e7IbSdeeFh2?id=1917731257870366808&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/raja-tertinggi-bengali-wo8igmPySx8?id=7173031800779295104&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/rebirth-of-citys-mad-doctor-bengali-oavcHx3NX24?id=3397326463182553456&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/dragon-arm-bengali-CjATQAiZLc6?id=5208719093385312344&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/my-homeless-billionaire-husband-bengali-ezUNgaWzE29?id=7589628630465511328&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/final-bharosa-bengali-EcglgvmYpX8?id=7518754110939055432&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/the-final-badla-bengali-e1BnsCu3d48?id=6771393998587674664&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/ek-anjani-shaadi-bengali-WrxwlIutwH6?id=5624981671536641048&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/revenge-of-my-fake-boyfriend-bengali-6dNHD2IVeq6?id=5391020440552981832&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/fake-boyfriend-bengali-el1ajeGpbh6?id=5268418846742003784&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/mafia-se-mohobbat-bengali-cyKUllMpYE4?id=3911872117998077808&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/my-top-secret-desire-bengali-0YWAvkmCZr4?id=3736152636412903744&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/my-doctor-boyfriend-bengali-GlcRODCHLH6?id=5628306525979559432&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/secret-billionaire-villager-bengali-IMXx3JiKfu7?id=6284646317004588736&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/ramayan-bengali-cwTk52t2eE8?id=7258943842622624088&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/revenge-of-xxl-husband-bengali-u1bWo1Vkk32?id=1723650464677351768&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/got-you-mr-always-right-bengali-caSHJsC5qA2?id=2171630482956469576&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/my-ceo-made-me-pregnant-bengali-mp1RCbLfTW?id=797215229972219584&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/rented-husband-bengali-Q0HlWDYnCj6?id=5301382205342730872&scene=&page_from=rank_detail&type=/movie/detail',
]

session = requests.Session()

def fetch_dynamic_token(base_domain):
    try:
        res = session.get(base_domain + '/', verify=False, timeout=8)
        html = res.text
        
        token = ''
        m_next = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        if m_next:
            m_tok = re.search(r'"token"\s*:\s*"([a-zA-Z0-9\.\-_]+)"', m_next.group(1), re.IGNORECASE)
            if m_tok:
                token = m_tok.group(1)
                
        if not token:
            m_tok_alt = re.search(r'"(?:accessToken|jwtToken|token)"\s*:\s*"([a-zA-Z0-9\.\-_]{20,})"', html, re.IGNORECASE)
            if m_tok_alt:
                token = m_tok_alt.group(1)
        
        return token
    except Exception as e:
        return ''

def get_stealth_headers(token='', base_domain='', referer=''):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="127", "Chromium";v="127", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }
    if base_domain:
        headers['Origin'] = base_domain
    if referer:
        headers['Referer'] = referer
    if token:
        headers['Authorization'] = 'Bearer ' + token
        
    return headers

def parse_target_url(url_or_path):
    parsed = urllib.parse.urlparse(url_or_path)
    query = urllib.parse.parse_qs(parsed.query)
    
    subject_id = query.get('id', [''])[0]
    if not subject_id:
        m = re.search(r'[?&]id=(\d+)', url_or_path, re.IGNORECASE)
        if m:
            subject_id = m.group(1)
    
    if not subject_id:
        return None
        
    raw_path = parsed.path if parsed.path else url_or_path
    path = '/' + raw_path.lstrip('/')
    
    sm = re.search(r'/(?:detail|movies)/([^/?#]+)', path, re.IGNORECASE)
    if sm:
        slug = sm.group(1)
    else:
        slug = os.path.basename(path)
        
    clean_title = re.sub(r'-[a-zA-Z0-9]+$', '', slug)
    clean_title = clean_title.replace('-', ' ').title()
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    
    return {
        'subjectId': str(subject_id),
        'title': clean_title if clean_title else ('Item ' + str(subject_id)),
        'detailPath': slug
    }

def fetch_subject_detail_with_fallback(movie_id, detail_path, token, config):
    detail_data = {}
    detail_page_url = f"{config['base_domain']}/detail/{detail_path}?id={movie_id}&scene=&page_from=rank_detail&type=/movie/detail"
    detail_url = f"{config['detail_api']}?subjectId={movie_id}&detailPath={urllib.parse.quote(detail_path)}"
    
    headers = get_stealth_headers(token, config['base_domain'], detail_page_url)
    
    try:
        res = session.get(detail_url, headers=headers, verify=False, timeout=8)
        if res.status_code == 200:
            json_resp = res.json()
            if json_resp.get('data') and isinstance(json_resp['data'], dict):
                detail_data = json_resp['data']
    except:
        pass
        
    poster_url = ''
    possible_cover_keys = ['cover', 'verticalCover', 'horizontalCover', 'poster', 'thumb', 'image', 'pic']
    for k in possible_cover_keys:
        if detail_data.get(k):
            val = detail_data[k]
            if isinstance(val, str) and re.match(r'^https?://', val, re.IGNORECASE):
                poster_url = val
                break
            if isinstance(val, dict) and val.get('url'):
                poster_url = val['url']
                break

    if not poster_url:
        try:
            html_headers = get_stealth_headers(token, config['base_domain'], config['base_domain'] + '/')
            res = session.get(detail_page_url, headers=html_headers, verify=False, timeout=10)
            html = res.text
            
            m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if m: poster_url = m.group(1).strip()
            
            if not poster_url:
                m = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                if m: poster_url = m.group(1).strip()
                
            if not poster_url:
                m = re.search(r'"cover"\s*:\s*\{"url"\s*:\s*"([^"]+)"', html, re.IGNORECASE)
                if m: poster_url = m.group(1).replace('\\/', '/')
                
            if not detail_data.get('title'):
                m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                if m: detail_data['title'] = m.group(1).strip()
                
            if not detail_data.get('description'):
                m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                if m: detail_data['description'] = m.group(1).strip()
                
        except:
            pass
            
    if poster_url:
        detail_data['resolvedPosterUrl'] = poster_url
        
    return detail_data

def fetch_stream_url_only(movie_id, se, ep, detail_path, token, config):
    play_api_url = f"{config['play_api']}?subjectId={movie_id}&se={se}&ep={ep}&detailPath={detail_path}&streamSignType=1&supportCodecs%5Bh264%5D=1"
    detail_page_url = f"{config['base_domain']}/movies/{detail_path}?id={movie_id}&type=/movie/detail&detailSe={se}&detailEp={ep}&lang=en"
    
    headers = get_stealth_headers(token, config['base_domain'], detail_page_url)
    
    try:
        res = session.get(play_api_url, headers=headers, verify=False, timeout=10)
        if res.status_code != 200:
            return None
        data = res.json()
    except:
        return None
        
    if not data or not data.get('data'):
        return None
        
    final_url = ''
    quality = 'HD'
    
    streams = data['data'].get('streams')
    if streams:
        mp4_list = {}
        for st in streams:
            if st.get('url'):
                res_val = int(st.get('resolutions', 0))
                mp4_list[res_val] = st
        if mp4_list:
            best_res = max(mp4_list.keys())
            best_mp4 = mp4_list[best_res]
            quality = f"{best_res}p"
            final_url = best_mp4['url']
    elif data['data'].get('dash') and data['data']['dash'][0].get('url'):
        quality = 'DASH'
        final_url = data['data']['dash'][0]['url']
        
    if not final_url:
        return None
        
    return {
        'url': final_url,
        'quality': quality
    }

def format_final_json(movie, series_data, config):
    detail = series_data.get('fullDetailData', {})
    title = series_data.get('resolvedTitle', movie.get('title', 'Unknown'))
    release_date = str(detail.get('releaseDate', detail.get('year', '')))
    
    year = ''
    yr_matches = re.search(r'\b(19\d{2}|20\d{2})\b', release_date)
    if yr_matches:
        year = yr_matches.group(1)
    else:
        movie_rd = str(movie.get('releaseDate', ''))
        yr_matches = re.search(r'\b(19\d{2}|20\d{2})\b', movie_rd)
        if yr_matches:
            year = yr_matches.group(1)
            
    clean_title = re.sub(r'^Watch\s+', '', title, flags=re.IGNORECASE)
    clean_title = re.sub(r'\s*Streaming\s+Online.*$', '', clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(r'\s*on\s+Movie[s]?Box.*$', '', clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(r'\[.*?\]', '', clean_title)
    clean_title = re.sub(r'\((?:19\d{2}|20\d{2})\)', '', clean_title)
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    
    final_title = f"{clean_title} ({year})" if year else clean_title
    
    poster = series_data.get('resolvedPoster', '')
    if not poster:
        poster = str(detail.get('resolvedPosterUrl', detail.get('cover', {}).get('url', detail.get('cover', ''))))
        
    raw_storyline = str(detail.get('description', detail.get('brief', '')))
    
    clean_storyline = re.sub(r'(?i)free\s+streaming\s+online\s+on\s+Movie[s]?Box', 'MY TV', raw_storyline)
    clean_storyline = re.sub(r'(?i)streaming\s+online\s+on\s+Movie[s]?Box', 'MY TV', clean_storyline)
    clean_storyline = re.sub(r'(?i)Movie[s]?Box', 'MY TV', clean_storyline)
    clean_storyline = re.sub(r'\s+', ' ', clean_storyline).strip()
    
    return {
        "category": str(config['category_name']),
        "director": "N/A",
        "genre": detail.get('genre', ["Drama"]) if detail.get('genre') else ["Drama"],
        "imdbRating": float(detail.get('imdbRatingValue', detail.get('score', 7.8))),
        "imdbVotes": int(detail.get('imdbRatingCount', 0)),
        "language": str(detail.get('language', 'Bengali')),
        "posterUrl": str(poster),
        "premium": False,
        "quality": str(series_data.get('quality', 'HD')),
        "releaseDate": str(release_date),
        "resolution": str(series_data.get('quality', 'HD')),
        "seasons": series_data.get('seasons', []),
        "sliderStatus": "off",
        "sliderUrl": "",
        "status": "on",
        "storyline": str(clean_storyline),
        "title": str(final_title),
        "triler": ""
    }

def get_combined_queue(target_list, config):
    items = []
    seen_ids = set()
    
    for url in target_list:
        parsed = parse_target_url(url)
        if parsed and parsed['subjectId'] not in seen_ids:
            seen_ids.add(parsed['subjectId'])
            items.append(parsed)
            
    try:
        headers = get_stealth_headers('', config['base_domain'])
        res = session.get(config['ranking_url'], headers=headers, verify=False, timeout=8)
        html = res.text
        
        matches = re.findall(r'href=["\'](?:/movies/|/detail/)?([^"\'?]+)\?id=(\d{18,20})[^"\']*["\']', html, re.IGNORECASE)
        for slug, subject_id in matches:
            slug = slug.strip('/')
            if subject_id not in seen_ids:
                seen_ids.add(subject_id)
                clean_name = re.sub(r'-[a-zA-Z0-9]+$', '', slug)
                clean_name = clean_name.replace('-', ' ').title()
                items.append({
                    'subjectId': subject_id,
                    'title': clean_name,
                    'detailPath': slug
                })
    except Exception as e:
        pass
        
    return items

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MovieBox Live Scraper</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0b0f19; color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 24px; line-height: 1.5; }
        .container { max-width: 960px; margin: 0 auto; background: #131b2e; border: 1px solid #1e293b; border-radius: 14px; padding: 28px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h1 { font-size: 24px; color: #38bdf8; display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
        .subtitle { color: #94a3b8; font-size: 14px; margin-bottom: 24px; }
        
        .progress-box { background: #0f172a; border: 1px solid #334155; padding: 18px; border-radius: 10px; margin-bottom: 22px; }
        .progress-header { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
        .progress-bar-bg { width: 100%; height: 12px; background: #1e293b; border-radius: 6px; overflow: hidden; }
        .progress-bar-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #38bdf8, #4ade80); transition: width 0.3s ease; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 22px; }
        .stat-card { background: #0f172a; border: 1px solid #1e293b; padding: 14px; border-radius: 8px; text-align: center; }
        .stat-card .num { font-size: 22px; font-weight: bold; color: #38bdf8; margin-top: 4px; }
        .stat-card .label { font-size: 12px; color: #64748b; text-transform: uppercase; }

        .terminal { background: #020617; border: 1px solid #1e293b; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 13px; height: 350px; overflow-y: auto; color: #cbd5e1; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; }
        .terminal .log-success { color: #4ade80; }
        .terminal .log-warn { color: #facc15; }
        .terminal .log-error { color: #f87171; }
        .terminal .log-info { color: #38bdf8; margin-top: 8px; }
        
        .ep-success { color: #4ade80; margin-right: 5px; font-weight: bold; }
        .ep-fail { color: #64748b; margin-right: 2px; font-weight: bold; font-size: 16px; }
        .inline-container { padding-left: 15px; margin-top: 2px; line-height: 1.8; }

        .controls { display: flex; gap: 12px; margin-top: 20px; align-items: center; }
        .btn { padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; font-size: 14px; transition: 0.2s; }
        .btn-primary { background: #0284c7; color: white; }
        .btn-primary:hover { background: #0369a1; }
        .btn-pause { background: #eab308; color: black; }
        .status-badge { font-size: 13px; padding: 6px 12px; border-radius: 20px; background: #1e293b; color: #38bdf8; }
    </style>
</head>
<body>

<div class="container">
    <h1>🚀 MovieBox Live Unlimited Scraper</h1>
    <div class="subtitle">Real-time Streaming Output • Anti-Timeout • Fetches Unlimited Episodes Gracefully</div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="label">Total Queue</div>
            <div class="num" id="stat-total">0</div>
        </div>
        <div class="stat-card">
            <div class="label">Processed</div>
            <div class="num" id="stat-processed">0</div>
        </div>
        <div class="stat-card">
            <div class="label">Saved Content</div>
            <div class="num" id="stat-saved" style="color: #4ade80;">0</div>
        </div>
        <div class="stat-card">
            <div class="label">Cooldown Break</div>
            <div class="num" id="stat-cooldown" style="color: #facc15;">2s</div>
        </div>
    </div>

    <div class="progress-box">
        <div class="progress-header">
            <span id="progress-status">Initializing Queue...</span>
            <span id="progress-percent">0%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" id="progress-fill"></div>
        </div>
    </div>

    <div class="terminal" id="term"></div>

    <div class="controls">
        <button class="btn btn-primary" id="btn-toggle" onclick="toggleScraper()">Pause Scraping</button>
        <div class="status-badge" id="engine-status">Engine Running...</div>
    </div>
</div>

<script>
let queue = [];
let currentIndex = 0;
let isPaused = false;
let maxRetries = 5;
let currentRetry = 0;
const cooldownMs = 2000;

const term = document.getElementById('term');
let currentInlineContainer = null;

function log(text, type = 'info') {
    const time = new Date().toLocaleTimeString();
    const span = document.createElement('div');
    span.className = 'log-' + type;
    span.innerHTML = `[${time}] ${text}`;
    term.appendChild(span);
    term.scrollTop = term.scrollHeight;
    currentInlineContainer = null; 
}

function logInline(text) {
    if (!currentInlineContainer) {
        currentInlineContainer = document.createElement('div');
        currentInlineContainer.className = 'inline-container';
        term.appendChild(currentInlineContainer);
    }
    currentInlineContainer.innerHTML += text;
    term.scrollTop = term.scrollHeight;
}

async function startEngine() {
    log("Loading target list...", "info");
    try {
        const res = await fetch('?action=get_queue');
        const data = await res.json();
        if (!data.success) throw new Error("Failed to load queue");

        queue = data.queue;
        document.getElementById('stat-total').innerText = queue.length;
        document.getElementById('stat-saved').innerText = data.saved_count;
        log(`Queue loaded: ${queue.length} items.`, "success");

        processNext();
    } catch (e) {
        log("Error loading queue. Retrying in 5s...", "error");
        setTimeout(startEngine, 5000);
    }
}

async function processNext() {
    if (isPaused) return;

    if (currentIndex >= queue.length) {
        document.getElementById('progress-status').innerText = "All items completed successfully!";
        document.getElementById('progress-percent').innerText = "100%";
        document.getElementById('progress-fill').style.width = "100%";
        document.getElementById('engine-status').innerText = "🎉 COMPLETED!";
        document.getElementById('engine-status').style.color = "#4ade80";
        log("🎉 ALL SCRAPING COMPLETED!", "success");
        return;
    }

    const item = queue[currentIndex];
    const itemNum = currentIndex + 1;
    const percent = Math.round((currentIndex / queue.length) * 100);

    document.getElementById('stat-processed').innerText = itemNum;
    document.getElementById('progress-status').innerText = `[${itemNum}/${queue.length}] ${item.title}`;
    document.getElementById('progress-percent').innerText = percent + "%";
    document.getElementById('progress-fill').style.width = percent + "%";

    log(`▶ [${itemNum}/${queue.length}] Scraping: <b>${item.title}</b>...`, "info");

    try {
        const res = await fetch(`?action=scrape_single&idx=${currentIndex}`);
        
        if (!res.ok) throw new Error(`Server Error ${res.status}`);
        
        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let finalData = null;
        let hasError = false;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            let lines = buffer.split('\\n');
            buffer = lines.pop(); 
            
            for (let line of lines) {
                line = line.trim();
                if (!line) continue;

                if (line.startsWith('LOG:')) {
                    log(line.substring(4), 'info');
                } else if (line.startsWith('INLINE:')) {
                    logInline(line.substring(7));
                } else if (line.startsWith('RESULT:')) {
                    finalData = JSON.parse(line.substring(7));
                } else if (line.startsWith('ERROR:')) {
                    const err = JSON.parse(line.substring(6));
                    hasError = true;
                    throw new Error(err.message);
                }
            }
        }

        if (finalData && finalData.success) {
            currentRetry = 0;
            log(`&nbsp;&nbsp;&nbsp;&nbsp;╰─ Success! ${finalData.episodes} Episodes Captured ✔`, "success");
            document.getElementById('stat-saved').innerText = finalData.total_saved;
            currentIndex++;
            setTimeout(processNext, cooldownMs);
        } else if (!hasError) {
            handleRetry("Stream completely timed out or crashed without error.");
        }
    } catch (err) {
        handleRetry(err.message);
    }
}

function handleRetry(reason) {
    currentRetry++;
    if (currentRetry <= maxRetries) {
        log(`&nbsp;&nbsp;&nbsp;&nbsp;⚠️ Glitch: ${reason}. Retry (${currentRetry}/${maxRetries}) in 5s...`, "warn");
        setTimeout(processNext, 5000);
    } else {
        log(`&nbsp;&nbsp;&nbsp;&nbsp;❌ Failed after ${maxRetries} attempts. Moving to next content.`, "error");
        currentRetry = 0;
        currentIndex++;
        setTimeout(processNext, 1000);
    }
}

function toggleScraper() {
    isPaused = !isPaused;
    const btn = document.getElementById('btn-toggle');
    if (isPaused) {
        btn.innerText = "Resume Scraping";
        btn.className = "btn btn-primary";
        document.getElementById('engine-status').innerText = "Paused";
        log("Scraper paused by user.", "warn");
    } else {
        btn.innerText = "Pause Scraping";
        btn.className = "btn btn-pause";
        document.getElementById('engine-status').innerText = "Engine Running...";
        log("Resuming scraping...", "info");
        processNext();
    }
}

window.onload = startEngine;
</script>
</body>
</html>"""

@app.route('/', methods=['GET'])
def index():
    action = request.args.get('action')
    
    if action == 'get_queue':
        queue = get_combined_queue(TARGET_CONTENT_LIST, CONFIG)
        
        saved_titles = {}
        if os.path.exists(CONFIG['output_file']):
            try:
                with open(CONFIG['output_file'], 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    for it in existing:
                        if it.get('title'):
                            saved_titles[it['title']] = True
            except:
                pass

        return jsonify({
            'success': True,
            'total': len(queue),
            'queue': queue,
            'saved_count': len(saved_titles),
            'saved_titles': list(saved_titles.keys())
        })

    elif action == 'scrape_single':
        idx = int(request.args.get('idx', 0))
        queue = get_combined_queue(TARGET_CONTENT_LIST, CONFIG)

        def generate_response():
            yield (" " * 1024) + "\n"

            if idx < 0 or idx >= len(queue):
                yield "ERROR:" + json.dumps({'message': 'Index out of bounds'}) + "\n"
                return

            movie = queue[idx]
            
            if not CONFIG['jwt_token']:
                CONFIG['jwt_token'] = fetch_dynamic_token(CONFIG['base_domain'])
                
            generator_obj = iter(fetch_series_seasons_and_episodes_generator(movie, CONFIG['jwt_token'], CONFIG))
            
            series_data = None
            try:
                while True:
                    result = next(generator_obj)
                    if isinstance(result, str):
                        yield result
                    elif isinstance(result, dict):
                        series_data = result
                        break
            except StopIteration:
                pass

            if not series_data or not series_data.get('seasons'):
                yield "ERROR:" + json.dumps({'message': 'No playable streams found'}) + "\n"
                return

            formatted = format_final_json(movie, series_data, CONFIG)

            all_data = []
            if os.path.exists(CONFIG['output_file']):
                try:
                    with open(CONFIG['output_file'], 'r', encoding='utf-8') as f:
                        all_data = json.load(f)
                except:
                    pass

            found_index = -1
            for k, item in enumerate(all_data):
                if item.get('title') == formatted.get('title'):
                    found_index = k
                    break

            if found_index >= 0:
                all_data[found_index] = formatted
            else:
                all_data.append(formatted)

            with open(CONFIG['output_file'], 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=4, ensure_ascii=False)

            yield "RESULT:" + json.dumps({
                'success': True,
                'title': formatted.get('title'),
                'poster': formatted.get('posterUrl'),
                'episodes': series_data.get('totalEpisodesFound'),
                'total_saved': len(all_data)
            }) + "\n"

        return Response(generate_response(), mimetype='text/plain', headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        })
        
    else:
        return HTML_TEMPLATE

def fetch_series_seasons_and_episodes_generator(movie, fallback_token, config):
    movie_id = str(movie.get('subjectId', movie.get('id', '')))
    title = movie.get('title', 'Unknown')
    detail_path = movie.get('detailPath', '')
    
    if not detail_path:
        detail_path = re.sub(r'[^A-Za-z0-9-]+', '-', title).strip('-').lower()
        
    full_detail_data = fetch_subject_detail_with_fallback(movie_id, detail_path, fallback_token, config)
    if full_detail_data.get('title'):
        title = full_detail_data['title']
        
    poster = full_detail_data.get('resolvedPosterUrl', '')
    
    seasons_array = []
    overall_quality = "HD"
    total_episodes_found = 0
    
    s_num = 1
    while s_num <= 50:
        episodes_array = []
        e_num = 1
        consecutive_fails = 0
        
        yield f"LOG:Scanning Season {s_num}...\n"
        
        while e_num <= 5000:
            stream_info = None
            attempts = 0
            
            while attempts < 3 and not (stream_info and stream_info.get('url')):
                stream_info = fetch_stream_url_only(movie_id, s_num, e_num, detail_path, fallback_token, config)
                if not (stream_info and stream_info.get('url')):
                    attempts += 1
                    if attempts < 3:
                        time.sleep(0.150)
            
            if not (stream_info and stream_info.get('url')) and s_num == 1 and e_num == 1:
                stream_info = fetch_stream_url_only(movie_id, 0, 0, detail_path, fallback_token, config)
                if stream_info and stream_info.get('url'):
                    e_num = 0
                    
            if stream_info and stream_info.get('url'):
                consecutive_fails = 0
                overall_quality = stream_info['quality']
                ep_title = "Full Movie" if e_num == 0 else f"Ep{e_num}"
                
                episodes_array.append({
                    "downStatus": "off",
                    "downUrl": stream_info['url'],
                    "duration": "--:--",
                    "episode_title": ep_title,
                    "headers": {
                        "Referer": config['base_domain'] + "/",
                        "Origin": "",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
                    },
                    "posterUrl": poster,
                    "streamUrl": stream_info['url'],
                    "view": 0
                })
                
                total_episodes_found += 1
                yield f"INLINE:<span class='ep-success'>{ep_title}✔</span> \n"
                
                if e_num == 0:
                    break
                e_num += 1
            else:
                consecutive_fails += 1
                yield "INLINE:<span class='ep-fail'>.</span>\n"
                
                if consecutive_fails >= 25:
                    break
                e_num += 1
                
            time.sleep(config['delay_between_episodes_ms'] / 1000.0)
            
        if episodes_array:
            season_title = "Movie Stream" if (e_num == 0 or (len(episodes_array) == 1 and episodes_array[0]['episode_title'] == 'Full Movie')) else f"Season {s_num}"
            seasons_array.append({
                "season_title": season_title,
                "episodes": episodes_array
            })
            
            if e_num == 0 or season_title == "Movie Stream":
                break
            s_num += 1
        else:
            break
            
    yield {
        'fullDetailData': full_detail_data,
        'seasons': seasons_array,
        'quality': overall_quality,
        'resolvedTitle': title,
        'resolvedPoster': poster,
        'totalEpisodesFound': total_episodes_found
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
