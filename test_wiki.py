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

assert clean('{{ubl|2022–present (China)|2024–present (Turkey)}}') == '2022–present (China); 2024–present (Turkey)', clean('{{ubl|2022–present (China)|2024–present (Turkey)}}')
assert clean('{{unbulleted list|2018–2020|{{start date|2021}}–present}}').startswith('2018–2020; 2021'), clean('{{unbulleted list|2018–2020|{{start date|2021}}–present}}')
assert years_in(clean('{{plainlist|\n* 2019–2023\n* 2024–present\n}}')) == [2019, 2023, 2024]
print('test_wiki: ubl/plainlist geçti')

ORNEK3 = """{{Infobox automobile
| name = Test
| production = {{ubl
|2018–2026 (China)<ref>{{cite web |url=http://x |title=a}}</ref>
|July 2017 – present<ref name="r">gerçek</ref>
}}
| model_years = 2019–present
| assembly = [[Kvasiny]], [[Czech Republic|Czechia]]
}}"""
f3 = infobox_fields(ORNEK3)
assert set(['name', 'production', 'model_years', 'assembly']) <= set(f3), list(f3)
assert years_in(clean(f3['production'])) == [2018, 2026, 2017], clean(f3['production'])
print('test_wiki: çok satırlı ubl geçti')
