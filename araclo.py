"""araclo.com model kronik sorun sayfalarının metnini indirir (ham veri toplama, ilk aşama).
Her model için cikti/araclo/<id>.txt yazar; sayfa yoksa durum 'yok' olur.
Ayrıştırma sonraki aşamada, gerçek sayfa yapısı görüldükten sonra yazılacak.
Nazik çalışır: robots.txt'e bakar, sayfalar arası 2 sn bekler, tek istek akışı."""
import html, json, os, re, sys, time, unicodedata, urllib.request, urllib.robotparser

BASE = 'https://www.araclo.com'
UA = 'otopuan-veri/1.0 (+https://github.com/MehmetBilalKAPLAN/otopuan-veri)'
SLUG = {'Mercedes-Benz': 'mercedes-benz', 'Citroen': 'citroen', 'MINI': 'mini', 'Volkswagen': 'volkswagen'}

def slug(s):
    s = s.lower().replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ş', 's').replace('ç', 'c').replace('ğ', 'g')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9.]+', '-', s).strip('-')

def adaylar(item):
    m = re.split(r'\s*[/(]', item['model'])[0].strip()
    b = SLUG.get(item['marka'], slug(item['marka']))
    return [f'{BASE}/vehicles/{b}-{slug(m)}/kronik-sorunlar']

def metin(h):
    h = re.sub(r'(?is)<(script|style|noscript|svg).*?</\1>', ' ', h)
    h = re.sub(r'(?i)</(p|div|li|h[1-6]|tr|section|article)>|<br\s*/?>', '\n', h)
    h = html.unescape(re.sub(r'<[^>]+>', ' ', h))
    return '\n'.join(x for x in (re.sub(r'[ \t]+', ' ', l).strip() for l in h.split('\n')) if x)

ARD = [0]

def indir(url, ham=None):
    if ham is not None: return 200, ham
    if ARD[0] >= 8: return 0, 'ag_kesildi'
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=15) as r:
            ARD[0] = 0
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception as e:
        ARD[0] += 1
        return 0, str(e)

def run(items, bekle=2.0, izin=None):
    os.makedirs('cikti/araclo', exist_ok=True)
    rp = urllib.robotparser.RobotFileParser(BASE + '/robots.txt')
    try: rp.read()
    except Exception: rp = None
    ozet = {}
    for it in items:
        durum = 'yok'
        for u in adaylar(it):
            if rp and not rp.can_fetch(UA, u): durum = 'robots_engeli'; break
            kod, h = indir(u)
            time.sleep(bekle)
            if kod == 200 and h:
                t = metin(h)
                open(f'cikti/araclo/{it["id"]}.txt', 'w', encoding='utf-8').write(u + '\n\n' + t)
                durum = 'tamam' if re.search(r'(?i)şiddet|kritik|sorun', t) else 'bos'
                break
            durum = f'http_{kod}'
        ozet[it['id']] = durum
        print(it['id'], durum, flush=True)
    return ozet

if __name__ == '__main__':
    items = json.load(open('modeller.json', encoding='utf-8'))
    from collections import Counter
    o = run(items)
    json.dump(o, open('cikti/araclo_durum.json', 'w'), indent=1)
    print('OZET', dict(Counter(o.values())))
