"""ABD NHTSA resmi geri çağırma kayıtlarını çeker (ücretsiz, anahtarsız API).
Kapsam: yalnızca ABD'de satılan model/yıllar. Türkiye'ye özgü modeller sonuçsuz kalır.
Çıktı: cikti/geri_cagirma.json  {id: {durum, sorgu, kayitlar:[...]}}"""
import json, re, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

API = 'https://api.nhtsa.gov/recalls/recallsByVehicle?'
MARKA = {'Mercedes-Benz': 'Mercedes-Benz', 'Citroen': 'Citroen', 'Skoda': 'Skoda', 'MINI': 'Mini', 'TOGG': None}
MODEL = {'Golf': 'Golf', 'ID.4 / ID.7': 'ID.4', 'C Serisi': 'C-Class', 'E Serisi': 'E-Class',
         'Sandero / Sandero Stepway': 'Sandero', 'Megane (Sedan / HB)': 'Megane'}

def sorgu_model(ad, marka):
    if ad in MODEL: return MODEL[ad]
    return re.split(r'\s*[/(]', ad)[0].strip()

ARD_HATA = [0]
HATALAR = []
SINIR = 20

def getir(url, deneme=2):
    if ARD_HATA[0] >= SINIR:
        return {'hata': 'ag_kesildi'}
    for i in range(deneme):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'otopuan-veri/1.0'}), timeout=10) as r:
                ARD_HATA[0] = 0
                return json.load(r)
        except Exception as e:
            son = type(e).__name__ + ': ' + str(e)[:120]
            if len(HATALAR) < 5: HATALAR.append(son + ' | ' + url[-70:])
            if not (isinstance(e, urllib.error.HTTPError) and 400 <= e.code < 500):
                ARD_HATA[0] += 1
            if isinstance(e, urllib.error.HTTPError) and 400 <= e.code < 500:
                return {'hata': son, 'kod': e.code}
            time.sleep(1)
    return {'hata': son}

def model_icin(item, yillar, bekle=0.3):
    marka = MARKA.get(item['marka'], item['marka'])
    if not marka:
        return {'durum': 'abd_yok', 'kayitlar': []}
    mdl = sorgu_model(item['model'], marka)
    kayit, gorulen, hata, yok400 = [], set(), 0, 0
    for y in yillar:
        d = getir(API + urllib.parse.urlencode({'make': marka, 'model': mdl, 'modelYear': y}))
        time.sleep(bekle)
        if 'hata' in d:
            hata += 1
            if d.get('kod') == 400: yok400 += 1
            continue
        for r in d.get('results', []):
            k = r.get('NHTSACampaignNumber')
            if k in gorulen: continue
            gorulen.add(k)
            kayit.append({'kampanya': k, 'yil': y, 'bilesen': r.get('Component', ''),
                          'ozet': (r.get('Summary') or '')[:300], 'sonuc': (r.get('Consequence') or '')[:200],
                          'tarih': r.get('ReportReceivedDate', ''),
                          'url': 'https://www.nhtsa.gov/?nhtsaId=' + str(k)})
    if yillar and yok400 == len(yillar):
        return {'durum': 'abd_yok', 'sorgu': marka + ' ' + mdl, 'kayitlar': []}
    durum = 'hata' if hata == len(yillar) and yillar else ('kayit_var' if kayit else 'kayit_yok')
    return {'durum': durum, 'sorgu': marka + ' ' + mdl, 'kayitlar': sorted(kayit, key=lambda x: x['tarih'], reverse=True)}

def run(items, bizim, bekle=0.15, isci=8):
    def is_(it):
        b = bizim.get(it['id'])
        yillar = list(range(max(b[0], 2015), min(b[1], 2026) + 1)) if b else []
        r = model_icin(it, yillar, bekle)
        print(it['id'], r['durum'], len(r['kayitlar']), flush=True)
        return it['id'], r
    with ThreadPoolExecutor(isci) as ex:
        return dict(ex.map(is_, items))

if __name__ == '__main__':
    items = json.load(open('modeller.json', encoding='utf-8'))
    bizim = json.load(open('bizim_yillar.json', encoding='utf-8'))
    s = run(items, bizim)
    json.dump({'kaynak': 'ABD NHTSA recallsByVehicle', 'guncelleme': time.strftime('%Y-%m-%d'), 'modeller': s},
              open('cikti/geri_cagirma.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    from collections import Counter
    print('OZET', dict(Counter(v['durum'] for v in s.values())))
    for h in HATALAR: print('HATA ORNEGI:', h)
