# F1 Telemetry Analyzer

F1 Telemetry Analyzer je Python aplikacija koja koristi FastF1 biblioteku za analizu stvarnih Formula 1 podataka. Program radi u komandnoj liniji i prikazuje telemetriju najbržeg kruga izabranog vozača.

## Funkcionalnosti

- izbor Formula 1 sezone
- izbor trke iz izabrane sezone
- izbor sesije: Race, Qualifying, FP1, FP2, FP3, Sprint i Sprint Qualifying
- izbor vozača
- pronalaženje najbržeg kruga vozača
- prikaz osnovnih podataka o krugu
- prikaz statistike telemetrije
- grafikon brzine
- grafikon gasa i kočenja
- grafikon brzine i obrtaja
- mapa staze obojena po brzini
- opciono poređenje brzine dva vozača
- opciono čuvanje grafikona u PNG formatu

Grafikoni se prikazuju nakon analize, a za svaki grafikon korisnik može izabrati da li želi da ga sačuva u folder `grafikoni`.

## Korišćene tehnologije

- Python
- FastF1
- Matplotlib
- Pandas
- NumPy
- pytest
- Ruff

## Struktura projekta

```text
f1_telemetry_analyzer/
├── analysis.py
├── app.py
├── charts.py
├── config.py
├── data.py
└── ui.py
tests/
├── test_analysis.py
└── test_config.py
```

Glavna logika je podeljena po odgovornostima: učitavanje podataka, analiza, prikaz u terminalu i generisanje grafikona. Fajl `f1_telemetry_analyzer.py` ostaje kompatibilna ulazna tačka za pokretanje aplikacije.

## Instalacija

Projekat zahteva Python i biblioteke navedene u fajlu `requirements.txt`.

```bash
pip install -r requirements.txt
```

Za razvoj i pokretanje testova:

```bash
pip install -e ".[dev]"
```

## Pokretanje

```bash
python f1_telemetry_analyzer.py
```

Alternativno, paket se može pokrenuti kao modul:

```bash
python -m f1_telemetry_analyzer
```

## Provere kvaliteta

Testovi i lintovanje mogu se pokrenuti komandama:

```bash
python -m pytest
ruff check .
```

Iste provere se automatski pokreću kroz GitHub Actions nakon svakog push-a ili pull requesta.

## Primer korišćenja

Tokom rada programa korisnik unosi:

```text
Sezona: 2023
Broj trke: 6
Tip sesije: R
Vozač: VER
```

Program zatim pronalazi najbrži krug izabranog vozača, prikazuje njegove osnovne podatke i statistiku, a zatim generiše grafikone telemetrije.

## Napomena

Prvo učitavanje podataka može potrajati jer FastF1 preuzima podatke sa interneta.

Podaci se čuvaju u `cache` folderu. Taj folder može biti veliki i automatski se kreira pri pokretanju programa.

Ako korisnik izabere čuvanje grafikona, PNG fajlovi se čuvaju u folderu `grafikoni`.

## Planirano dalje

- poređenje vremena po sektorima, a ne samo ukupnog vremena kruga
- web interfejs u Streamlit-u umesto komandne linije
- analiza strategije guma tokom cele trke
- poređenje više od dva vozača istovremeno

<img width="1899" height="921" alt="Screenshot 2026-08-17 123141" src="https://github.com/user-attachments/assets/cca09485-82dc-4054-bf8e-93e7ace269b4" />
<img width="1475" height="731" alt="Screenshot 2026-08-17 123126" src="https://github.com/user-attachments/assets/52f0a222-7866-4972-bd92-c0d9aacf2295" />
<img width="1437" height="730" alt="Screenshot 2026-08-17 123106" src="https://github.com/user-attachments/assets/9ef5f933-1aed-4f62-a06b-f895a4ac357f" />
<img width="1446" height="709" alt="Screenshot 2026-08-17 114829" src="https://github.com/user-attachments/assets/88e4bb28-de0f-4579-943a-5434bdc1bb42" />
