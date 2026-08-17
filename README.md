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

## Planirano dalje
 Poređenje vremena po sektorima (ne samo ukupnog kruga),
 Web interfejs (Streamlit) umesto komandne linije,
 Analiza strategije guma tokom cele trke,
 Poređenje više od dva vozača istovremeno.

<img width="1899" height="921" alt="Screenshot 2026-08-17 123141" src="https://github.com/user-attachments/assets/cca09485-82dc-4054-bf8e-93e7ace269b4" />
<img width="1475" height="731" alt="Screenshot 2026-08-17 123126" src="https://github.com/user-attachments/assets/52f0a222-7866-4972-bd92-c0d9aacf2295" />
<img width="1437" height="730" alt="Screenshot 2026-08-17 123106" src="https://github.com/user-attachments/assets/9ef5f933-1aed-4f62-a06b-f895a4ac357f" />
<img width="1446" height="709" alt="Screenshot 2026-08-17 114829" src="https://github.com/user-attachments/assets/88e4bb28-de0f-4579-943a-5434bdc1bb42" />
