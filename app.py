import requests
import re
import json
import time
import html
import urllib3
from urllib.parse import quote, urlparse, parse_qs

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

req_session = requests.Session()

# ---------------- CONFIGURATION ---------------- #
config = {
    'base_domain': 'https://themoviebox.xyz',
    'ranking_path': '/ranking-list/eL6uk3fbsY4?id=4175575772020854200&page_from=more_SUBJECTS_MOVIE',
    'output_file': 'scraped_data_output.json',
    'category_name': 'Bengali Collection',
    'delay_between_episodes_s': 0.15,
    'cooldown_seconds': 2,
    'jwt_token': ''
}

config['ranking_url'] = config['base_domain'] + config['ranking_path']
config['detail_api'] = config['base_domain'] + '/wefeed-h5api-bff/subject/detail'
config['play_api'] = config['base_domain'] + '/wefeed-h5api-bff/subject/play'

target_content_list = [
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
    'detail/rented-husband-bengali-Q0HlWDYnCj6?id=5301382205342730872&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/fake-boyfriend-bengali-el1ajeGpbh6?id=5268418846742003784&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/mafia-se-mohobbat-bengali-cyKUllMpYE4?id=3911872117998077808&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/my-top-secret-desire-bengali-0YWAvkmCZr4?id=3736152636412903744&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/my-doctor-boyfriend-bengali-GlcRODCHLH6?id=5628306525979559432&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/secret-billionaire-villager-bengali-IMXx3JiKfu7?id=6284646317004588736&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/ramayan-bengali-cwTk52t2eE8?id=7258943842622624088&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/revenge-of-xxl-husband-bengali-u1bWo1Vkk32?id=1723650464677351768&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/got-you-mr-always-right-bengali-caSHJsC5qA2?id=2171630482956469576&scene=&page_from=rank_detail&type=/movie/detail',
    'detail/my-ceo-made-me-pregnant-bengali-mp1RCbLfTW?id=797215229972219584&scene=&page_from=rank_detail&type=/movie/detail'
]

# ---------------- CORE FUNCTIONS ---------------- #
def get_stealth_headers(token='', referer=''):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Origin': config['base_domain']
    }
    if referer: headers['Referer'] = referer
    if token: headers['Authorization'] = f'Bearer {token}'
    return headers

def fetch_dynamic_token():
    try:
        res = req_session.get(config['base_domain'] + '/', headers=get_stealth_headers(), verify=False, timeout=10)
        html_content = res.text
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_content, re.I | re.S)
        if m:
            tm = re.search(r'"token"\s*:\s*"([a-zA-Z0-9\.\-_]+)"', m.group(1), re.I)
            if tm: return tm.group(1)
        fm = re.search(r'"(?:accessToken|jwtToken|token)"\s*:\s*"([a-zA-Z0-9\.\-_]{20,})"', html_content, re.I)
        if fm: return fm.group(1)
    except Exception as e:
        print(f"Token Error: {e}")
    return ""

def parse_target_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    subject_id = query.get('id', [''])[0]
    if not subject_id:
        m = re.search(r'[?&]id=(\d+)', url)
        if m: subject_id = m.group(1)
    if not subject_id: return None
    
    path = parsed.path if parsed.path else url
    m = re.search(r'/(?:detail|movies)/([^/?#]+)', path, re.I)
    slug = m.group(1) if m else path.split('/')[-1]
    
    clean_title = re.sub(r'-[a-zA-Z0-9]+$', '', slug).replace('-', ' ').title()
    clean_title = " ".join(clean_title.split())
    
    return {'subjectId': subject_id, 'title': clean_title or f'Item {subject_id}', 'detailPath': slug}

def fetch_subject_detail(movie):
    detail_data = {}
    movie_id, detail_path = movie['subjectId'], movie['detailPath']
    detail_page_url = f"{config['base_domain']}/detail/{detail_path}?id={movie_id}&scene=&page_from=rank_detail&type=/movie/detail"
    
    api_url = f"{config['detail_api']}?subjectId={movie_id}&detailPath={quote(detail_path)}"
    try:
        res = req_session.get(api_url, headers=get_stealth_headers(config['jwt_token'], detail_page_url), verify=False, timeout=10)
        if res.status_code == 200:
            json_data = res.json()
            if 'data' in json_data and isinstance(json_data['data'], dict):
                detail_data = json_data['data']
    except Exception: pass

    # SSR Poster Fallback Logic
    poster_url = ""
    for k in ['cover', 'verticalCover', 'horizontalCover', 'poster', 'thumb', 'image', 'pic']:
        if k in detail_data and detail_data[k]:
            if isinstance(detail_data[k], str) and detail_data[k].startswith('http'):
                poster_url = detail_data[k]; break
            if isinstance(detail_data[k], dict) and detail_data[k].get('url'):
                poster_url = detail_data[k]['url']; break

    if not poster_url:
        try:
            html_res = req_session.get(detail_page_url, headers=get_stealth_headers(config['jwt_token']), verify=False, timeout=10)
            if html_res.status_code == 200:
                html_txt = html_res.text
                og_img = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html_txt, re.I)
                if og_img: poster_url = html.unescape(og_img.group(1).strip())
                
                if not poster_url:
                    tw_img = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', html_txt, re.I)
                    if tw_img: poster_url = html.unescape(tw_img.group(1).strip())
                
                if not poster_url:
                    js_img = re.search(r'"cover"\s*:\s*\{"url"\s*:\s*"([^"]+)"', html_txt, re.I)
                    if js_img: poster_url = js_img.group(1).replace('\\/', '/')
                    
                if not detail_data.get('title'):
                    og_title = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', html_txt, re.I)
                    if og_title: detail_data['title'] = html.unescape(og_title.group(1).strip())
                    
                if not detail_data.get('description'):
                    og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', html_txt, re.I)
                    if og_desc: detail_data['description'] = html.unescape(og_desc.group(1).strip())
        except Exception: pass

    if poster_url: detail_data['resolvedPosterUrl'] = poster_url
    return detail_data

def fetch_stream_url(movie_id, se, ep, detail_path):
    play_url = f"{config['play_api']}?subjectId={movie_id}&se={se}&ep={ep}&detailPath={detail_path}&streamSignType=1&supportCodecs%5Bh264%5D=1"
    page_url = f"{config['base_domain']}/movies/{detail_path}?id={movie_id}&type=/movie/detail&detailSe={se}&detailEp={ep}&lang=en"
    
    try:
        res = req_session.get(play_url, headers=get_stealth_headers(config['jwt_token'], page_url), verify=False, timeout=10)
        if res.status_code == 200:
            data = res.json().get('data', {})
            streams = data.get('streams', [])
            if streams:
                best_stream = sorted(streams, key=lambda x: int(x.get('resolutions', 0)), reverse=True)[0]
                return {'url': best_stream.get('url', ''), 'quality': str(best_stream.get('resolutions', 'HD')) + 'p'}
            dash = data.get('dash', [])
            if dash and dash[0].get('url'):
                return {'url': dash[0]['url'], 'quality': 'DASH'}
    except Exception: pass
    return None

def fetch_episodes(movie):
    movie_id, detail_path = movie['subjectId'], movie['detailPath']
    detail_data = fetch_subject_detail(movie)
    poster = detail_data.get('resolvedPosterUrl', '')
    
    seasons_array = []
    total_found = 0
    overall_quality = "HD"
    
    for s_num in range(1, 21):
        episodes_array = []
        e_num = 1
        consecutive_fails = 0
        
        while e_num <= 250:
            stream_info = None
            attempts = 0
            
            while attempts < 3 and not stream_info:
                stream_info = fetch_stream_url(movie_id, s_num, e_num, detail_path)
                if not stream_info:
                    attempts += 1
                    if attempts < 3: time.sleep(0.15)
            
            # Fallback for S0 E0 Movies
            if not stream_info and s_num == 1 and e_num == 1:
                stream_info = fetch_stream_url(movie_id, 0, 0, detail_path)
                if stream_info and stream_info['url']:
                    e_num = 0
            
            if stream_info and stream_info.get('url'):
                consecutive_fails = 0
                overall_quality = stream_info['quality']
                ep_title = "Full Movie" if e_num == 0 else f"E{e_num}"
                
                episodes_array.append({
                    "downStatus": "off",
                    "downUrl": stream_info['url'],
                    "duration": "--:--",
                    "episode_title": ep_title,
                    "headers": {
                        "Referer": config['base_domain'] + "/",
                        "Origin": "",
                        "User-Agent": get_stealth_headers()['User-Agent']
                    },
                    "posterUrl": poster,
                    "streamUrl": stream_info['url'],
                    "view": 0
                })
                total_found += 1
                if e_num == 0: break
                e_num += 1
            else:
                consecutive_fails += 1
                if consecutive_fails >= 2: break
                e_num += 1
            
            time.sleep(config['delay_between_episodes_s'])
            
        if episodes_array:
            season_title = "Movie Stream" if (e_num == 0 or (len(episodes_array) == 1 and episodes_array[0]['episode_title'] == 'Full Movie')) else f"Season {s_num}"
            seasons_array.append({"season_title": season_title, "episodes": episodes_array})
            if e_num == 0 or season_title == "Movie Stream": break
        else: break
        
    return {
        'detail_data': detail_data,
        'seasons': seasons_array,
        'quality': overall_quality,
        'poster': poster,
        'total_found': total_found
    }

def format_json(movie, series_data):
    detail = series_data['detail_data']
    raw_title = detail.get('title') or movie['title']
    release_date = str(detail.get('releaseDate', detail.get('year', '')))
    
    year = ""
    yr_match = re.search(r'\b(19\d{2}|20\d{2})\b', release_date)
    if yr_match: year = yr_match.group(1)
    
    clean_title = re.sub(r'(?i)^Watch\s+', '', raw_title)
    clean_title = re.sub(r'(?i)\s*Streaming\s+Online.*$', '', clean_title)
    clean_title = re.sub(r'(?i)\s*on\s+Movie[s]?Box.*$', '', clean_title)
    clean_title = re.sub(r'\[.*?\]', '', clean_title)
    clean_title = re.sub(r'\((?:19\d{2}|20\d{2})\)', '', clean_title)
    clean_title = " ".join(clean_title.split())
    
    final_title = f"{clean_title} ({year})" if year else clean_title
    
    poster = series_data['poster'] or str(detail.get('resolvedPosterUrl', ''))
    
    raw_story = str(detail.get('description', detail.get('brief', '')))
    clean_story = re.sub(r'(?i)free\s+streaming\s+online\s+on\s+Movie[s]?Box', 'MY TV', raw_story)
    clean_story = re.sub(r'(?i)streaming\s+online\s+on\s+Movie[s]?Box', 'MY TV', clean_story)
    clean_story = re.sub(r'(?i)Movie[s]?Box', 'MY TV', clean_story)
    clean_story = " ".join(clean_story.split())

    return {
        "category": config['category_name'],
        "director": "N/A",
        "genre": detail.get('genre', ["Drama"]),
        "imdbRating": float(detail.get('imdbRatingValue', detail.get('score', 7.8))),
        "imdbVotes": int(detail.get('imdbRatingCount', 0)),
        "language": str(detail.get('language', 'Bengali')),
        "posterUrl": poster,
        "premium": False,
        "quality": series_data['quality'] or "HD",
        "releaseDate": release_date,
        "resolution": series_data['quality'] or "HD",
        "seasons": series_data['seasons'],
        "sliderStatus": "off",
        "sliderUrl": "",
        "status": "on",
        "storyline": clean_story,
        "title": final_title,
        "triler": ""
    }

def get_combined_queue():
    seen = set()
    queue = []
    
    for url in target_content_list:
        parsed = parse_target_url(url)
        if parsed and parsed['subjectId'] not in seen:
            seen.add(parsed['subjectId'])
            queue.append(parsed)
            
    try:
        res = req_session.get(config['ranking_url'], headers=get_stealth_headers(), verify=False, timeout=10)
        if res.status_code == 200:
            matches = re.finditer(r'href=["\'](?:/movies/|/detail/)?([^"\'?]+)\?id=(\d{18,20})[^"\']*["\']', res.text, re.I)
            for m in matches:
                slug, sub_id = m.group(1).strip('/'), m.group(2)
                if sub_id not in seen:
                    seen.add(sub_id)
                    clean_name = re.sub(r'-[a-zA-Z0-9]+$', '', slug).replace('-', ' ').title()
                    queue.append({'subjectId': sub_id, 'title': " ".join(clean_name.split()), 'detailPath': slug})
    except Exception: pass
    return queue

# ---------------- CLI ENGINE ---------------- #
if __name__ == '__main__':
    print("====================================================")
    print("  MovieBox Python Auto-Scraper (GitHub Actions)")
    print("====================================================")
    
    if not config['jwt_token']:
        config['jwt_token'] = fetch_dynamic_token()
        print("[+] Dynamic Auth Token Extracted.")
        
    queue = get_combined_queue()
    total = len(queue)
    print(f"Total Targets in Queue: {total}\n")
    
    all_data = []
    try:
        with open(config['output_file'], 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    except: pass

    for idx, movie in enumerate(queue):
        print(f"[{idx+1}/{total}] Fetching: {movie['title']}...")
        
        retries = 0
        success = False
        while retries < 3 and not success:
            series_data = fetch_episodes(movie)
            
            if series_data['seasons']:
                formatted = format_json(movie, series_data)
                
                # Update existing or append new
                found_idx = next((i for i, item in enumerate(all_data) if item['title'] == formatted['title']), -1)
                if found_idx >= 0: all_data[found_idx] = formatted
                else: all_data.append(formatted)
                
                with open(config['output_file'], 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=4, ensure_ascii=False)
                    
                print(f"  [DONE] Episodes: {series_data['total_found']} | Poster: {'YES' if formatted['posterUrl'] else 'NO'}")
                success = True
            else:
                retries += 1
                print(f"  ⚠️ Stream missed, pausing 4s before retry ({retries}/3)...")
                time.sleep(4)
                
        time.sleep(config['cooldown_seconds'])
        
    print(f"\n🎉 UPDATE COMPLETE! Total {len(all_data)} items saved to {config['output_file']}")
