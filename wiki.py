"""Wikipedia'dan (MediaWiki API) araç sayfalarının wikitext'ini çekip üretim yıllarını ayıklar.
Yalnızca standart kütüphane kullanır. Kaynak: Wikipedia (CC BY-SA); her çıktıya sayfa bağlantısı eklenir."""
import json, re, time, urllib.parse, urllib.request

UA = 'OtoPuanVeri/0.1 (https://github.com/MehmetBilalKAPLAN/otopuan-veri)'
API = 'https://en.wikipedia.org/w/api.php'
# Anlam ayrımı sayfasına giden bağlantıların elle düzeltmesi (id -> sayfa)
WK_DUZELTME = {'egeacross': 'Fiat_Tipo_(2015)', 'jazz': 'Honda_Fit'}

def wikitext(title):
    q = urllib.parse.urlencode({'action': 'parse', 'page': title.replace('_', ' '), 'prop': 'wikitext',
                                'format': 'json', 'redirects': 1, 'formatversion': 2})
    req = urllib.request.Request(API + '?' + q, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if 'error' in d:
        raise RuntimeError(d['error'].get('info', 'hata'))
    return d['parse']['title'], d['parse']['wikitext']

def split_fields(block):
    """Bilgi kutusu bloğunu üst düzey '| ad = değer' alanlarına ayırır; iç içe {{...}} ve [[...]] içindeki '|' işaretlerini bölmez."""
    fields, depth_c, depth_b, cur = {}, 0, 0, []
    i, n = 0, len(block)
    parts, buf = [], ''
    while i < n:
        two = block[i:i + 2]
        if two == '{{': depth_c += 1; buf += two; i += 2; continue
        if two == '}}': depth_c -= 1; buf += two; i += 2; continue
        if two == '[[': depth_b += 1; buf += two; i += 2; continue
        if two == ']]': depth_b -= 1; buf += two; i += 2; continue
        ch = block[i]
        if ch == '|' and depth_c == 1 and depth_b == 0:
            parts.append(buf); buf = ''
        else:
            buf += ch
        i += 1
    parts.append(buf)
    for p in parts[1:]:
        if '=' in p:
            k, v = p.split('=', 1)
            k = k.strip().lower()
            if k and '{' not in k and '[' not in k:
                fields[k] = v.strip()
    return fields

def infobox_fields(text):
    """İlk {{Infobox automobile ...}} bloğundaki alanları sözlük olarak döndürür."""
    m = re.search(r'\{\{\s*Infobox (?:automobile|car)\b', text, re.I)
    if not m:
        return {}
    i, depth, start = m.start(), 0, m.start()
    j = i
    while j < len(text) - 1:
        if text[j:j + 2] == '{{':
            depth += 1; j += 2
        elif text[j:j + 2] == '}}':
            depth -= 1; j += 2
            if depth == 0:
                break
        else:
            j += 1
    block = text[start:j]
    f = split_fields(block)
    return {k: (v[:-2].rstrip() if v.endswith('}}') and v.count('{{') < v.count('}}') else v) for k, v in f.items()}

def all_infoboxes(text):
    """Sayfadaki tüm {{Infobox automobile}} bloklarını (nesil bölümlerinde de bulunur) alan sözlükleri olarak döndürür."""
    out, pos = [], 0
    while True:
        m = re.search(r'\{\{\s*Infobox (?:automobile|car)\b', text[pos:], re.I)
        if not m:
            break
        start = pos + m.start(); j = start; depth = 0
        while j < len(text) - 1:
            if text[j:j + 2] == '{{':
                depth += 1; j += 2
            elif text[j:j + 2] == '}}':
                depth -= 1; j += 2
                if depth == 0:
                    break
            else:
                j += 1
        block = text[start:j]
        f = split_fields(block)
        out.append({k: (v[:-2].rstrip() if v.endswith('}}') and v.count('{{') < v.count('}}') else v) for k, v in f.items()})
        pos = max(j, start + 2)
    return out

def clean(v):
    v = re.sub(r'<ref[^>]*?/>|<ref[^>]*?>.*?</ref>', '', v, flags=re.S)
    v = re.sub(r'\{\{\s*(?:start date|end date)[^|}]*\|(\d{4})[^}]*\}\}', r'\1', v, flags=re.I)
    v = re.sub(r'\{\{\s*(?:nowrap|nobr)\s*\|([^}]*)\}\}', r'\1', v, flags=re.I)
    for _ in range(4):
        v2 = re.sub(r'\{\{\s*(?:unbulleted list|ubl|plainlist|flatlist|hlist|ublist|unbulleted)\s*\|([^{}]*)\}\}',
                    lambda m: '; '.join(x.strip(' *') for x in m.group(1).split('|') if x.strip(' *')), v, flags=re.I)
        if v2 == v:
            break
        v = v2
    v = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', v)
    v = re.sub(r'<br\s*/?>', '; ', v)
    v = re.sub(r"'''?|<[^>]+>", '', v)
    return re.sub(r'\s+', ' ', v).strip()

def years_in(s):
    return [int(x) for x in re.findall(r'\b(19[5-9]\d|20[0-4]\d)\b', s)]

def generations(text):
    """Başlıklarda 'generation' geçen ve yıl içeren satırları döndürür (nesil adayları)."""
    out = []
    for m in re.finditer(r'^(=+)\s*(.+?)\s*=+\s*$', text, re.M):
        h = clean(m.group(2))
        if re.search(r'generation|facelift|mk\s?\d|\(\w*\d{4}', h, re.I) and years_in(h):
            out.append(h)
    return out

def probe(title):
    page_title, text = wikitext(title)
    f = infobox_fields(text)
    prod = clean(f.get('production', ''))
    kutular = all_infoboxes(text)
    if not prod:
        for b in kutular:
            p = clean(b.get('production', ''))
            if p:
                prod = p; break
    if not prod:
        m = re.search(r'\|\s*production\s*=\s*(.+)', text)
        if m:
            prod = clean(m.group(1))
    return {
        'ham_alanlar': sorted(f.keys())[:25],
        'sayfa': page_title,
        'url': 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(page_title.replace(' ', '_')),
        'uretim': prod,
        'uretim_yillari': years_in(prod),
        'model_yillari': clean(f.get('model_years', '')),
        'nesil_basliklari': generations(text),
        'bilgi_kutulari': [{'ad': clean(b.get('name', '')), 'uretim': clean(b.get('production', '')),
                            'model_yillari': clean(b.get('model_years', ''))} for b in all_infoboxes(text)],
    }

def search_titles(q, n=5):
    qs = urllib.parse.urlencode({'action': 'query', 'list': 'search', 'srsearch': q, 'srlimit': n,
                                 'format': 'json', 'formatversion': 2})
    req = urllib.request.Request(API + '?' + qs, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return [x['title'] for x in d.get('query', {}).get('search', [])]

def probe_with_fallback(title, ad):
    """Önce verilen sayfayı dener; bilgi kutusu/üretim yoksa (ör. anlam ayrımı sayfası) arama sonuçlarını sırayla dener."""
    r = probe(title)
    if r['uretim_yillari']:
        return r
    for t in search_titles(ad + ' car'):
        time.sleep(0.5)
        try:
            r2 = probe(t)
        except Exception:
            continue
        if r2['uretim_yillari']:
            r2['yedek_arama'] = 'sayfa ' + title + ' yerine ' + t + ' kullanıldı'
            return r2
    return r

def run(items, wait=1.0):
    out = []
    for it in items:
        try:
            r = probe_with_fallback(WK_DUZELTME.get(it['id'], it['wk']), it['marka'] + ' ' + it['model'].split('(')[0].strip())
            r.update({'id': it['id'], 'marka': it['marka'], 'model': it['model']})
        except Exception as e:
            r = {'id': it['id'], 'marka': it['marka'], 'model': it['model'], 'hata': str(e)}
        out.append(r)
        time.sleep(wait)
    return out
