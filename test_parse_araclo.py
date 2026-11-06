import parse_araclo as p
t = """https://www.araclo.com/vehicles/x-y/kronik-sorunlar
X Y Kronik Sorunları
2 bilinen sorun · önem sırasıyla · nesle göre
Y I (A) 2016–2019 2 sorun
Neslin tamamında · 1
Orta Klima kondenserinin delinmesi 2016–2019 Onarım maliyeti orta
Belirtiler
Klima zayıflar
Alırken kontrol edin
Klimayı çalıştırın
Hatchback gövdesinde · 1
Kritik Yakıt pompası arızası 2018–2019 Onarım maliyeti düşük
Belirtiler
Motor tekler
Alırken kontrol edin
Geri çağırma sorun
"""
r = p.parse(t)
assert r['durum'] == 'tamam' and len(r['kayitlar']) == 2 and r['ozet_sayi'] == 2, r
assert r['kayitlar'][1]['kapsam'] == 'Hatchback gövdesinde' and r['kayitlar'][1]['sev'] == 'Kritik'
assert p.parse('x\nKayıtlı sorun yok\n')['durum'] == 'kayit_yok'
t2 = "u\nbilinen\n23 bilinen sorun · x\nToyota-1.5 motorunda · 1\nYüksek Hibrit batarya kapasite kaybı 150.000 km sonrası Onarım maliyeti yüksek\nBelirtiler\na\nAlırken kontrol edin\nb\n"
r2 = p.parse(t2); assert r2['kayitlar'][0]['yil'] == '150.000 km sonrası', r2
print('parse_araclo testleri tamam')
