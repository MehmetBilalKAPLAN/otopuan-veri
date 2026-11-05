import araclo
assert araclo.adaylar({'marka': 'Honda', 'model': 'Civic'}) == ['https://www.araclo.com/vehicles/honda-civic/kronik-sorunlar']
assert araclo.adaylar({'marka': 'Mercedes-Benz', 'model': 'C Serisi'})[0].endswith('mercedes-benz-c-serisi/kronik-sorunlar')
assert araclo.adaylar({'marka': 'Kia', 'model': 'Sorento (Hibrit)'})[0].endswith('kia-sorento/kronik-sorunlar')
t = araclo.metin('<script>x</script><div>Yakıt <b>pompası</b></div><li>Şiddet: Kritik</li>')
assert 'Yakıt pompası' in t and 'Şiddet: Kritik' in t and 'x' not in t.split('\n')[0], t
print('araclo testleri tamam')
