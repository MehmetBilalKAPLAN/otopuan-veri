"""Wikipedia'dan (MediaWiki API) araç sayfalarının wikitext'ini çekip üretim yıllarını ayıklar.
Yalnızca standart kütüphane kullanır. Kaynak: Wikipedia (CC BY-SA); her çıktıya sayfa bağlantısı eklenir."""
import json, re, time, urllib.parse, urllib.request

UA = 'OtoPuanVeri/0.1 (https://github.com/MehmetBilalKAPLAN/otopuan-veri)'
API = 'https://en.wikipedia.org/w/api.php'

def wikitext(title):
    q = urllib.parse.urlencode({'action': 'parse', 'page': title.replace('_', ' '), 'prop': 'wikitext',
                                'format': 'json', 'redirects': 1, 'formatversion': 2})
    req = urllib.request.Request(API + '?' + q, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if 'error' in d:
        raise RuntimeError(d['error'].get('info', 'hata'))
    return d['parse']['title'], d['parse']['wikitext']

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
    if block.endswith('}}'): block = block[:-2]
    fields = {}
    for line in re.split(r'\n\s*\|', block)[1:]:
        if '=' in line:
            k, v = line.split('=', 1)
            fields[k.strip().lower()] = v.strip()
    return fields

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
        if block.endswith('}}'): block = block[:-2]
        fields = {}
        for line in re.split(r'\n\s*\|', block)[1:]:
            if '=' in line:
                k, v = line.split('=', 1); fields[k.strip().lower()] = v.strip()
        out.append(fields); pos = max(j, start + 2)
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

def run(items, wait=1.0):
    out = []
    for it in items:
        try:
            r = probe(it['wk'])
            r.update({'id': it['id'], 'marka': it['marka'], 'model': it['model']})
        except Exception as e:
            r = {'id': it['id'], 'marka': it['marka'], 'model': it['model'], 'hata': str(e)}
        out.append(r)
        time.sleep(wait)
    return out
