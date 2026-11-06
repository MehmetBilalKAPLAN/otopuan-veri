import nhtsa
calls = []
def fake(url, deneme=3):
    calls.append(url)
    if 'Civic' in url and 'modelYear=2020' in url:
        return {'results': [{'NHTSACampaignNumber': '20V001', 'Component': 'AIR BAGS', 'Summary': 's', 'Consequence': 'c', 'ReportReceivedDate': '01/02/2020'}]}
    if 'Civic' in url and 'modelYear=2021' in url:
        return {'results': [{'NHTSACampaignNumber': '20V001', 'Component': 'AIR BAGS'}]}
    return {'results': []}
nhtsa.getir = fake
r = nhtsa.model_icin({'id': 'civic', 'marka': 'Honda', 'model': 'Civic'}, [2020, 2021, 2022], 0)
assert r['durum'] == 'kayit_var' and len(r['kayitlar']) == 1, r
assert nhtsa.model_icin({'id': 't', 'marka': 'TOGG', 'model': 'T10X'}, [2024], 0)['durum'] == 'abd_yok'
assert nhtsa.sorgu_model('Golf', '') == 'Golf' and nhtsa.sorgu_model('Tiggo 7 (Pro)', '') == 'Tiggo 7'
nhtsa.getir = lambda u, d=3: {'hata': 'x'}
assert nhtsa.model_icin({'id': 'a', 'marka': 'Honda', 'model': 'Civic'}, [2020], 0)['durum'] == 'hata'
nhtsa.getir = lambda u, d=3: {'hata': 'HTTP 400', 'kod': 400}
assert nhtsa.model_icin({'id': 'a', 'marka': 'Dacia', 'model': 'Duster'}, [2020, 2021], 0)['durum'] == 'abd_yok'
print('nhtsa testleri tamam')
