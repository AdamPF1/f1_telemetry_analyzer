# F1 Telemetry Analyzer

F1 Telemetry Analyzer je Python projekat koji koristi FastF1 biblioteku za analizu stvarnih Formula 1 podataka.

## Funkcionalnosti

- izbor Formula 1 sezone
- izbor trke iz izabrane sezone
- izbor sesije: Race, Qualifying, FP1, FP2, FP3, Sprint
- izbor vozača
- pronalaženje najbržeg kruga vozača
- prikaz osnovnih podataka o krugu
- prikaz telemetrije
- grafikon brzine
- grafikon gasa i kočenja
- grafikon brzine i obrtaja
- mapa staze obojena po brzini

## Korišćene tehnologije

- Python
- FastF1
- Matplotlib
- Pandas
- NumPy

## Instalacija
bash pip install -r requirements.txt

## Pokretanje
bash python f1_telemetry_analyzer.py

## Primer korišćenja
text Sezona: 2023 Trka: 6 Sesija: R Vozač: VER


Program zatim prikazuje telemetriju najbržeg kruga izabranog vozača.

## Napomena

Prvo učitavanje podataka može potrajati jer FastF1 preuzima podatke sa interneta.

Podaci se čuvaju u `cache` folderu. Taj folder se ne objavljuje na GitHub jer može biti veliki i može se ponovo napraviti pri pokretanju programa.