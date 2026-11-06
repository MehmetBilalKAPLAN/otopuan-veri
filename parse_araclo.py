"""araclo.com kronik sorun sayfası metnini (cikti/araclo/<id>.txt) yapılandırılmış kayıtlara çevirir."""
import json, os, re, sys
SEV = r'(Kritik|Yüksek|Orta|Düşük)'
RE_GEN = re.compile(r'^(.+?) (\d{4})[–-](\d{4}) (\d+) sorun$')
RE_GRP = re.compile(r'^(.+?) · (\d+)$')
RE_ISS = re.compile(r'^' + SEV + r' (.+?)(?: (\d{4}(?:[–-]\d{4})?|\d[\d.]* km sonrası|\d[\d.]*[–-]\d[\d.]* km))? Onarım maliyeti (\S+)$')

def parse(text):
    L = [x.strip() for x in text.split('\n')]
    url = L[0]
    out = {'url': url, 'durum': 'bilinmiyor', 'kayitlar': [], 'ozet_sayi': None, 'sorun_satiri': 0}
    if any(x == 'Kayıtlı sorun yok' for x in L):
        out['durum'] = 'kayit_yok'; return out
    start = next((i for i, x in enumerate(L) if re.match(r'^\d+ bilinen sorun', x)), None)
    if start is None: return out
    out['ozet_sayi'] = int(re.match(r'^(\d+)', L[start]).group(1))
    gen = {'ad': None, 'bas': None, 'bit': None}; grp = None; i = start + 1
    while i < len(L):
        x = L[i]
        if x.startswith('Araclo') and i > start + 5 and 'Otomobil platformu' in (L[i+1] if i+1 < len(L) else ''): break
        m = RE_GEN.match(x)
        if m: gen = {'ad': m.group(1), 'bas': int(m.group(2)), 'bit': int(m.group(3))}; grp = None; i += 1; continue
        m = RE_GRP.match(x)
        if m and not RE_ISS.match(x): grp = m.group(1); i += 1; continue
        m = RE_ISS.match(x)
        if m:
            sev, title, yil, maliyet = m.groups()
            bel = kon = ''
            j = i + 1
            while j < len(L) and j < i + 6:
                if L[j] == 'Belirtiler' and j + 1 < len(L): bel = L[j+1]; j += 2; continue
                if L[j] == 'Alırken kontrol edin' and j + 1 < len(L): kon = L[j+1]; j += 2; break
                break
            out['kayitlar'].append({'sev': sev, 'baslik': title, 'yil': yil, 'maliyet': maliyet, 'nesil': gen['ad'],
                                    'nesil_bas': gen['bas'], 'nesil_bit': gen['bit'], 'kapsam': grp or 'Neslin tamamında',
                                    'belirti': bel, 'kontrol': kon})
            i = j; continue
        i += 1
    out['durum'] = 'tamam' if out['kayitlar'] else 'ayristirilamadi'
    return out

if __name__ == '__main__':
    d = sys.argv[1]; res = {}
    for f in sorted(os.listdir(d)):
        if f.endswith('.txt'):
            res[f[:-4]] = parse(open(os.path.join(d, f), encoding='utf-8').read())
    json.dump(res, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    import collections
    print(collections.Counter(v['durum'] for v in res.values()))
    for k, v in res.items():
        if v['durum'] == 'tamam' and v['ozet_sayi'] != len({(r['nesil'], r['kapsam'], r['baslik']) for r in v['kayitlar']}) + 0:
            pass
