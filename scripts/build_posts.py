# Gera a lista compacta de posts (POSTS.items) a partir das respostas brutas da API de posts.
# Uso: python3 scripts/build_posts.py pagina1.json pagina2.json ... > posts.json
import json, sys, re
def load(f):
    d = json.load(open(f))
    d = d.get('data', d)
    return d['results']['posts']
def ptype(p):
    pl = p['platform']; m = p.get('media') or []
    vid = any('video' in (x.get('type') or '') for x in m); n = len(m)
    link = p.get('previewLink') or ''
    if pl == 'instagram':
        t = (p.get('instagramPostDetails') or {}).get('type') or p.get('type')
        if t == 'reel': return 'Reels'
        if t == 'story': return 'Story'
    if pl == 'youtube':
        yt = (p.get('youtubePostDetails') or {}).get('type')
        return 'Shorts' if (yt == 'short' or '/shorts/' in link) else 'Vídeo'
    if pl == 'facebook' and ((p.get('facebookPostDetails') or {}).get('type') == 'reel' or p.get('type') == 'reel'):
        return 'Reels'
    if vid: return 'Vídeo'
    if n > 1: return 'Carrossel'
    if n == 1: return 'Imagem'
    return 'Texto'
def title(s):
    s = (s or '').strip()
    first = re.split(r'\n', s)[0].strip()
    first = re.sub(r'\s+', ' ', first)
    return (first[:110] + '…') if len(first) > 110 else first
seen = set(); out = []
for f in sys.argv[1:]:
    for p in load(f):
        if p.get('status') != 'published' or p.get('deleted') or p['_id'] in seen: continue
        seen.add(p['_id'])
        i = p.get('insights') or {}
        out.append({'n': p['platform'], 't': ptype(p), 'd': (p.get('publishedAt') or p.get('displayDate'))[:10],
                    'c': title(p.get('summary')), 'u': p.get('previewLink') or '',
                    'l': int(i.get('like') or 0), 'm': int(i.get('comment') or 0), 's': int(i.get('share') or 0)})
out.sort(key=lambda x: x['d'], reverse=True)
print(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
