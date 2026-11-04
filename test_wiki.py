"""Ağ gerektirmeyen birim test (uydurma örnek metinle ayrıştırıcıyı sınar)."""
from wiki import infobox_fields, clean, years_in, generations
ORNEK = """{{Infobox automobile
| name = Örnek Model
| production = {{start date|2018}}–present<ref>kaynak</ref>
| model_years = 2019–present
}}
== Eighth generation (E210; 2018) ==
== Tarih ==
=== Facelift (2022) ===
"""
f = infobox_fields(ORNEK)
assert clean(f['production']) == '2018–present', clean(f['production'])
assert years_in(clean(f['production'])) == [2018]
assert generations(ORNEK) == ['Eighth generation (E210; 2018)', 'Facelift (2022)'], generations(ORNEK)
print('test_wiki: tümü geçti')
from wiki import all_infoboxes
ORNEK2 = ORNEK + "\n{{Infobox automobile\n| name = Nesil 2\n| production = 2022–2025\n}}\n"
ib = all_infoboxes(ORNEK2)
assert len(ib) == 2 and clean(ib[1]['production']) == '2022–2025', ib
print('test_wiki: çoklu bilgi kutusu geçti')
