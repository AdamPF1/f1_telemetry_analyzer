import os

import fastf1
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

CACHE_FOLDER = "cache"


def ukljuciCache():
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)
    fastf1.Cache.enable_cache(CACHE_FOLDER)


def prikaziNaslov():
    print("----------------------------------------")
    print("           F1 Telemetry Analyzer         ")
    print("----------------------------------------")
    print("Ovaj program koristi stvarne Formula 1 podatke.")
    print("Možeš da izabereš sezonu, trku, sesiju i vozača.")
    print("Program zatim prikazuje telemetriju njegovog najbržeg kruga.")


def unesiSezonu():
    while True:
        try:
            sezona = int(input("\nUnesi sezonu, na primer 2022, ali takođe možeš bilo koju od 2018 pa nadalje: "))
            if sezona < 2018:
                print("Preporuka je da koristiš sezonu od 2018. pa nadalje zbog boljih podataka.")
            else:
                return sezona
        except ValueError:
            print("Greška: moraš uneti broj, na primer 2024.")


def prikaziTrkeUSezoni(sezona):
    try:
        kalendar = fastf1.get_event_schedule(sezona)
    except Exception as greska:
        print("Došlo je do greške pri učitavanju kalendara.")
        print(greska)
        return None
    print(f"\n--- Trke u sezoni {sezona} ---")
    for _, trka in kalendar.iterrows():
        brojRunde = trka["RoundNumber"]
        nazivTrke = trka["EventName"]
        lokacija = trka["Location"]
        if brojRunde != 0:
            print(f"{brojRunde}. {nazivTrke} - {lokacija}")
    return kalendar


def izaberiTrku(kalendar):
    while True:
        try:
            brojTrke = int(input("\nUnesi broj trke koju želiš da analiziraš: "))
            izabranaTrka = kalendar[kalendar["RoundNumber"] == brojTrke]
            if izabranaTrka.empty:
                print("Ne postoji trka sa tim brojem. Pokušaj ponovo.")
            else:
                return brojTrke
        except ValueError:
            print("Greška: moraš uneti broj trke.")


def izaberiTipSesije():
    dostupneSesije = ["R", "Q", "FP1", "FP2", "FP3", "S", "SQ"]
    print("\n--- Izbor sesije ---")
    print("R   - Race / Trka")
    print("Q   - Qualifying / Kvalifikacije")
    print("FP1 - Prvi trening")
    print("FP2 - Drugi trening")
    print("FP3 - Treći trening")
    print("S   - Sprint")
    print("SQ  - Sprint Shootout / Sprint kvalifikacije")
    while True:
        sesija = input("Unesi tip sesije: ").upper()
        if sesija in dostupneSesije:
            return sesija
        print("Nepoznata sesija. Pokušaj ponovo.")


def ucitajSesiju(sezona, brojTrke, tipSesije):
    print("\nUčitavam podatke...")
    print("Ako prvi put učitavaš ovu trku, može da potraje malo duže.")
    try:
        sesija = fastf1.get_session(sezona, brojTrke, tipSesije)
        sesija.load()
    except Exception as greska:
        print("Došlo je do greške pri učitavanju sesije.")
        print("Mogući razlozi:")
        print("- nema interneta")
        print("- podaci za tu sesiju nisu dostupni")
        print("- izabrana trka nema taj tip sesije")
        print(greska)
        return None
    print("Podaci su uspešno učitani.")
    return sesija


def prikaziVozace(sesija):
    print("\n--- Vozači dostupni u ovoj sesiji ---")
    if sesija.results is not None and not sesija.results.empty:
        for _, vozac in sesija.results.iterrows():
            skracenica = vozac["Abbreviation"]
            punoIme = vozac["FullName"]
            tim = vozac["TeamName"]
            print(f"{skracenica} - {punoIme} | {tim}")
    else:
        vozaci = sorted(sesija.laps["Driver"].dropna().unique())
        for vozac in vozaci:
            print(vozac)


def izaberiVozaca(sesija):
    dostupniVozaci = sorted(sesija.laps["Driver"].dropna().unique())
    while True:
        vozac = input("\nUnesi skraćenicu vozača, na primer VER, HAM, LEC, NOR: ").upper()
        if vozac in dostupniVozaci:
            return vozac
        print("Vozač nije pronađen u ovoj sesiji. Pokušaj ponovo.")


def pronadjiNajbrziKrug(sesija, vozac):
    krugoviVozaca = sesija.laps.pick_drivers(vozac)
    if krugoviVozaca.empty:
        print("Nema dostupnih krugova za ovog vozača.")
        return None
    najbrziKrug = krugoviVozaca.pick_fastest()
    if najbrziKrug is None:
        print("Nije moguće pronaći najbrži krug za ovog vozača.")
        return None
    return najbrziKrug


def prikaziOsnovnePodatkeOKrugu(najbrziKrug, vozac):
    vremeKruga = najbrziKrug["LapTime"]
    brojKruga = najbrziKrug["LapNumber"]
    tipGuma = najbrziKrug["Compound"]
    pozicija = najbrziKrug["Position"]
    print("\n--- Podaci o najbržem krugu ---")
    print(f"Vozač: {vozac}")
    print(f"Broj kruga: {int(brojKruga)}")
    print(f"Vreme kruga: {vremeKruga}")
    print(f"Gume: {tipGuma}")
    if not np.isnan(pozicija):
        print(f"Pozicija na stazi u tom trenutku: {int(pozicija)}")


def nacrtajBrzinu(telemetrija, vozac):
    plt.figure(figsize=(12, 6))
    plt.plot(
        telemetrija["Distance"],
        telemetrija["Speed"],
        color="red",
        linewidth=2
    )
    plt.title(f"Brzina kroz najbrži krug - {vozac}")
    plt.xlabel("Distanca kroz krug u metrima")
    plt.ylabel("Brzina u km/h")
    plt.grid(True)
    plt.show()


def nacrtajGasIKocenje(telemetrija, vozac):
    plt.figure(figsize=(12, 6))
    plt.plot(
        telemetrija["Distance"],
        telemetrija["Throttle"],
        label="Gas",
        color="green",
        linewidth=2
    )
    plt.plot(
        telemetrija["Distance"],
        telemetrija["Brake"] * 100,
        label="Kočenje",
        color="red",
        linewidth=2
    )
    plt.title(f"Gas i kočenje kroz najbrži krug - {vozac}")
    plt.xlabel("Distanca kroz krug u metrima")
    plt.ylabel("Procenat")
    plt.legend()
    plt.grid(True)
    plt.show()


def nacrtajBrzinuIObrtaje(telemetrija, vozac):
    figura, prvaOsa = plt.subplots(figsize=(12, 6))
    prvaOsa.plot(
        telemetrija["Distance"],
        telemetrija["Speed"],
        color="red",
        label="Brzina"
    )
    prvaOsa.set_xlabel("Distanca kroz krug u metrima")
    prvaOsa.set_ylabel("Brzina u km/h", color="red")
    prvaOsa.tick_params(axis="y", labelcolor="red")
    prvaOsa.grid(True)
    drugaOsa = prvaOsa.twinx()
    drugaOsa.plot(
        telemetrija["Distance"],
        telemetrija["RPM"],
        color="blue",
        label="Obrtaji"
    )
    drugaOsa.set_ylabel("RPM / obrtaji motora", color="blue")
    drugaOsa.tick_params(axis="y", labelcolor="blue")
    plt.title(f"Brzina i obrtaji kroz najbrži krug - {vozac}")
    figura.tight_layout()
    plt.show()


def nacrtajMapuStazePoBrzini(telemetrija, vozac):
    x = np.array(telemetrija["X"].values)
    y = np.array(telemetrija["Y"].values)
    brzina = np.array(telemetrija["Speed"].values)
    tacke = np.array([x, y]).T.reshape(-1, 1, 2)
    segmenti = np.concatenate([tacke[:-1], tacke[1:]], axis=1)
    figura, osa = plt.subplots(figsize=(10, 8))
    normala = plt.Normalize(brzina.min(), brzina.max())
    linije = LineCollection(segmenti, cmap="plasma", norm=normala)
    linije.set_array(brzina)
    linije.set_linewidth(5)
    osa.add_collection(linije)
    osa.set_xlim(x.min() - 500, x.max() + 500)
    osa.set_ylim(y.min() - 500, y.max() + 500)
    osa.set_title(f"Mapa staze po brzini - {vozac}")
    osa.axis("off")
    colorbar = figura.colorbar(linije, ax=osa)
    colorbar.set_label("Brzina u km/h")
    plt.show()


def prikaziStatistikuTelemetrije(telemetrija, vozac):
    maksimalnaBrzina = telemetrija["Speed"].max()
    prosecnaBrzina = telemetrija["Speed"].mean()
    maksimalniGas = telemetrija["Throttle"].max()
    prosecniGas = telemetrija["Throttle"].mean()
    brojKocenja = telemetrija["Brake"].sum()
    print("\n--- Kratka statistika telemetrije ---")
    print(f"Vozač: {vozac}")
    print(f"Maksimalna brzina: {maksimalnaBrzina:.2f} km/h")
    print(f"Prosečna brzina: {prosecnaBrzina:.2f} km/h")
    print(f"Maksimalni gas: {maksimalniGas:.2f}%")
    print(f"Prosečni gas: {prosecniGas:.2f}%")
    print(f"Broj tačaka gde je vozač kočio: {brojKocenja}")


def analizirajVozaca(sesija, vozac):
    najbrziKrug = pronadjiNajbrziKrug(sesija, vozac)
    if najbrziKrug is None:
        return False
    prikaziOsnovnePodatkeOKrugu(najbrziKrug, vozac)
    try:
        telemetrija = najbrziKrug.get_telemetry()
    except Exception as greska:
        print("Telemetrija nije mogla da se učita za ovog vozača.")
        print("Možeš probati drugog vozača iz iste sesije.")
        print(greska)
        return False
    if telemetrija.empty:
        print("Telemetrija nije dostupna za ovaj krug.")
        print("Možeš probati drugog vozača iz iste sesije.")
        return False
    prikaziStatistikuTelemetrije(telemetrija, vozac)
    nacrtajBrzinu(telemetrija, vozac)
    nacrtajGasIKocenje(telemetrija, vozac)
    nacrtajBrzinuIObrtaje(telemetrija, vozac)
    nacrtajMapuStazePoBrzini(telemetrija, vozac)
    return True


def korisnikZeliDrugogVozaca():
    while True:
        izbor = input("\nDa li želiš da probaš drugog vozača iz iste sesije? da/ne: ").lower()
        if izbor == "da":
            return True
        elif izbor == "ne":
            return False
        else:
            print("Unesi 'da' ili 'ne'.")


def main():
    ukljuciCache()
    prikaziNaslov()
    sezona = unesiSezonu()
    kalendar = prikaziTrkeUSezoni(sezona)
    if kalendar is None:
        return
    brojTrke = izaberiTrku(kalendar)
    tipSesije = izaberiTipSesije()
    sesija = ucitajSesiju(sezona, brojTrke, tipSesije)
    if sesija is None:
        return
    prikaziVozace(sesija)
    while True:
        vozac = izaberiVozaca(sesija)
        analizaUspesna = analizirajVozaca(sesija, vozac)
        if analizaUspesna:
            break
        if not korisnikZeliDrugogVozaca():
            print("Analiza je prekinuta.")
            break

if __name__ == "__main__":
    main()
