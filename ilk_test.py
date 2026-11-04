"""İlk deneme: birkaç modelin Wikipedia sayfasından üretim yıllarını çeker ve ekrana yazar.
Kullanım:  python ilk_test.py            (varsayılan 8 model)
           python ilk_test.py corolla clio egea"""
import json, sys, io
from wiki import run

sys.stdout.reconfigure(encoding='utf-8')
items = json.load(open('modeller.json', encoding='utf-8'))
secilen = sys.argv[1:] or ['corolla', 'clio', 'egea', 'golf', 'togg', 't10x', 'qashqai', 'i20']
liste = [i for i in items if i['id'] in secilen]
print(len(liste), 'model denenecek...\n')
sonuc = run(liste)
for r in sonuc:
    print('=' * 60)
    print(r['marka'], r['model'])
    if 'hata' in r:
        print('  HATA:', r['hata']); continue
    print('  sayfa      :', r['url'])
    print('  üretim     :', r['uretim'] or '(bulunamadı)')
    print('  model yılı :', r['model_yillari'] or '-')
    print('  nesil başl.:', ' | '.join(r['nesil_basliklari'][:8]) or '-')
json.dump(sonuc, open('cikti/ilk_test.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nKaydedildi: cikti/ilk_test.json')
