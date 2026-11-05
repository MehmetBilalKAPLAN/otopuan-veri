"""131 modelin tamamını Wikipedia'dan çeker, bizim yıl tablosuyla karşılaştırır.
Kullanım: python hepsi.py          (yaklaşık 3-4 dakika)
Çıktı: cikti/nesiller.json (ham veri), cikti/karsilastirma.csv, ekrana kısa özet."""
import csv, json, re, sys
from wiki import run, years_in

sys.stdout.reconfigure(encoding='utf-8')
items = json.load(open('modeller.json', encoding='utf-8'))
bizim = json.load(open('bizim_yillar.json', encoding='utf-8'))   # id -> [bas, bit, durum]
sonuc = run(items, wait=1.0)
json.dump(sonuc, open('cikti/nesiller.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def parse_range(s):
    """'2015-2026; ...' / '2018-present' -> (baslangic, bitis|None=devam)"""
    ys = years_in(s)
    if not ys:
        return None, None
    devam = bool(re.search(r'present|günümüz|ongoing|current', s, re.I))
    return min(ys), (None if devam else max(ys))

rows, ozet = [], {'uyumlu': 0, 'celiski': 0, 'belirsiz': 0, 'hata': 0}
for r in sonuc:
    b = bizim.get(r['id'])
    if 'hata' in r:
        ozet['hata'] += 1
        rows.append([r['id'], r['marka'], r['model'], b, '', '', 'hata', r['hata']]); continue
    wb, we = parse_range(r['uretim'])
    ranges = [parse_range(k['uretim']) for k in r.get('bilgi_kutulari', [])] + [(wb, we)]
    starts = sorted({x[0] for x in ranges if x[0]})
    gen_starts = sorted(set(starts) | {y for h in r['nesil_basliklari'] for y in years_in(h)[:1]})
    durum, neden = 'belirsiz', 'Wikipedia yılı bulunamadı | ham üretim: ' + repr(r['uretim'])[:60] + ' | alanlar: ' + ','.join(r.get('ham_alanlar', [])[:12])
    if b and wb:
        frm, to = b[0], b[1]
        if frm < wb:
            durum, neden = 'celiski', f'bizim başlangıç {frm}, Wikipedia üretim başlangıcı {wb}'
        elif we and to > we + 1:
            durum, neden = 'celiski', f'bizim bitiş {to}, Wikipedia üretim bitişi {we}'
        elif any(abs(frm - g) <= 1 for g in gen_starts):
            durum, neden = 'uyumlu', f'başlangıç {frm}, bir nesil başlangıcıyla (±1) uyumlu: {gen_starts}'
        else:
            durum, neden = 'belirsiz', f'başlangıç {frm} hiçbir nesil başlangıcıyla eşleşmiyor: {gen_starts}'
    ozet[{'uyumlu': 'uyumlu', 'celiski': 'celiski'}.get(durum, 'belirsiz')] += 1
    rows.append([r['id'], r['marka'], r['model'], b, r['uretim'], ' | '.join(map(str, gen_starts)), durum, neden])

with open('cikti/karsilastirma.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'marka', 'model', 'bizim_yil', 'wikipedia_uretim', 'nesil_baslangiclari', 'durum', 'neden']); w.writerows(rows)

print('ÖZET:', ozet)
print('\n--- ÇELİŞKİ ve HATA satırları (bunları Claude\'a yapıştırın) ---')
for r in rows:
    if r[6] in ('celiski', 'hata'):
        print(r[0], '|', r[1], r[2], '| bizim', r[3], '| wiki', r[4], '|', r[7])
print('\n--- BELİRSİZ ---')
for r in rows:
    if r[6] == 'belirsiz':
        print(r[0], '|', r[3], '|', r[4], '|', r[7])
