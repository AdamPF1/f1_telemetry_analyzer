import os

import fastf1
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

CACHE_FOLDER = "cache"


def ukljuci_cache():
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)

    fastf1.Cache.enable_cache(CACHE_FOLDER)


def prikazi_naslov():
    print("----------------------------------------")
    print("           F1 Telemetry Analyzer         ")
    print("----------------------------------------")
    print("Ovaj program koristi stvarne Formula 1 podatke.")
    print("Možeš da izabereš sezonu, trku, sesiju i vozača.")
    print("Program zatim prikazuje telemetriju njegovog najbržeg kruga.")


def unesi_sezonu():
    while True:
        try:
            sezona = int(input("\nUnesi sezonu, na primer 2022, 2023 ili 2024: "))

            if sezona < 2018:
                print("Preporuka je da koristiš sezonu od 2018. pa nadalje zbog boljih podataka.")
            else:
                return sezona

        except ValueError:
            print("Greška: moraš uneti broj, na primer 2024.")


def prikazi_trke_u_sezoni(sezona):
    try:
        kalendar = fastf1.get_event_schedule(sezona)
    except Exception as greska:
        print("Došlo je do greške pri učitavanju kalendara.")
        print(greska)
        return None

    print(f"\n--- Trke u sezoni {sezona} ---")

    for _, trka in kalendar.iterrows():
        broj_runde = trka["RoundNumber"]
        naziv_trke = trka["EventName"]
        lokacija = trka["Location"]

        if broj_runde != 0:
            print(f"{broj_runde}. {naziv_trke} - {lokacija}")

    return kalendar


def izaberi_trku(kalendar):
    while True:
        try:
            broj_trke = int(input("\nUnesi broj trke koju želiš da analiziraš: "))

            izabrana_trka = kalendar[kalendar["RoundNumber"] == broj_trke]

            if izabrana_trka.empty:
                print("Ne postoji trka sa tim brojem. Pokušaj ponovo.")
            else:
                return broj_trke

        except ValueError:
            print("Greška: moraš uneti broj trke.")


def izaberi_tip_sesije():
    dostupne_sesije = ["R", "Q", "FP1", "FP2", "FP3", "S", "SQ"]

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

        if sesija in dostupne_sesije:
            return sesija

        print("Nepoznata sesija. Pokušaj ponovo.")


def ucitaj_sesiju(sezona, broj_trke, tip_sesije):
    print("\nUčitavam podatke...")
    print("Ako prvi put učitavaš ovu trku, može da potraje malo duže.")

    try:
        sesija = fastf1.get_session(sezona, broj_trke, tip_sesije)
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


def prikazi_vozace(sesija):
    print("\n--- Vozači dostupni u ovoj sesiji ---")

    if sesija.results is not None and not sesija.results.empty:
        for _, vozac in sesija.results.iterrows():
            skracenica = vozac["Abbreviation"]
            puno_ime = vozac["FullName"]
            tim = vozac["TeamName"]

            print(f"{skracenica} - {puno_ime} | {tim}")
    else:
        vozaci = sorted(sesija.laps["Driver"].dropna().unique())

        for vozac in vozaci:
            print(vozac)


def izaberi_vozaca(sesija):
    dostupni_vozaci = sorted(sesija.laps["Driver"].dropna().unique())

    while True:
        vozac = input("\nUnesi skraćenicu vozača, na primer VER, HAM, LEC, NOR: ").upper()

        if vozac in dostupni_vozaci:
            return vozac

        print("Vozač nije pronađen u ovoj sesiji. Pokušaj ponovo.")


def pronadji_najbrzi_krug(sesija, vozac):
    krugovi_vozaca = sesija.laps.pick_drivers(vozac)

    if krugovi_vozaca.empty:
        print("Nema dostupnih krugova za ovog vozača.")
        return None

    najbrzi_krug = krugovi_vozaca.pick_fastest()

    if najbrzi_krug is None:
        print("Nije moguće pronaći najbrži krug za ovog vozača.")
        return None

    return najbrzi_krug


def prikazi_osnovne_podatke_o_krugu(najbrzi_krug, vozac):
    vreme_kruga = najbrzi_krug["LapTime"]
    broj_kruga = najbrzi_krug["LapNumber"]
    komponenta_guma = najbrzi_krug["Compound"]
    pozicija = najbrzi_krug["Position"]

    print("\n--- Podaci o najbržem krugu ---")
    print(f"Vozač: {vozac}")
    print(f"Broj kruga: {int(broj_kruga)}")
    print(f"Vreme kruga: {vreme_kruga}")
    print(f"Gume: {komponenta_guma}")

    if not np.isnan(pozicija):
        print(f"Pozicija na stazi u tom trenutku: {int(pozicija)}")


def nacrtaj_brzinu(telemetrija, vozac):
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


def nacrtaj_gas_i_kocenje(telemetrija, vozac):
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


def nacrtaj_brzinu_i_obrtaje(telemetrija, vozac):
    figura, prva_osa = plt.subplots(figsize=(12, 6))

    prva_osa.plot(
        telemetrija["Distance"],
        telemetrija["Speed"],
        color="red",
        label="Brzina"
    )

    prva_osa.set_xlabel("Distanca kroz krug u metrima")
    prva_osa.set_ylabel("Brzina u km/h", color="red")
    prva_osa.tick_params(axis="y", labelcolor="red")
    prva_osa.grid(True)

    druga_osa = prva_osa.twinx()

    druga_osa.plot(
        telemetrija["Distance"],
        telemetrija["RPM"],
        color="blue",
        label="Obrtaji"
    )

    druga_osa.set_ylabel("RPM / obrtaji motora", color="blue")
    druga_osa.tick_params(axis="y", labelcolor="blue")

    plt.title(f"Brzina i obrtaji kroz najbrži krug - {vozac}")
    figura.tight_layout()

    plt.show()


def nacrtaj_mapu_staze_po_brzini(telemetrija, vozac):
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


def prikazi_statistiku_telemetrije(telemetrija, vozac):
    maksimalna_brzina = telemetrija["Speed"].max()
    prosecna_brzina = telemetrija["Speed"].mean()
    maksimalni_gas = telemetrija["Throttle"].max()
    prosecni_gas = telemetrija["Throttle"].mean()
    broj_kocenja = telemetrija["Brake"].sum()

    print("\n--- Kratka statistika telemetrije ---")
    print(f"Vozač: {vozac}")
    print(f"Maksimalna brzina: {maksimalna_brzina:.2f} km/h")
    print(f"Prosečna brzina: {prosecna_brzina:.2f} km/h")
    print(f"Maksimalni gas: {maksimalni_gas:.2f}%")
    print(f"Prosečni gas: {prosecni_gas:.2f}%")
    print(f"Broj tačaka gde je vozač kočio: {broj_kocenja}")


def analiziraj_vozaca(sesija, vozac):
    najbrzi_krug = pronadji_najbrzi_krug(sesija, vozac)

    if najbrzi_krug is None:
        return False

    prikazi_osnovne_podatke_o_krugu(najbrzi_krug, vozac)

    try:
        telemetrija = najbrzi_krug.get_telemetry()
    except Exception as greska:
        print("Telemetrija nije mogla da se učita za ovog vozača.")
        print("Možeš probati drugog vozača iz iste sesije.")
        print(greska)
        return False

    if telemetrija.empty:
        print("Telemetrija nije dostupna za ovaj krug.")
        print("Možeš probati drugog vozača iz iste sesije.")
        return False

    prikazi_statistiku_telemetrije(telemetrija, vozac)

    nacrtaj_brzinu(telemetrija, vozac)
    nacrtaj_gas_i_kocenje(telemetrija, vozac)
    nacrtaj_brzinu_i_obrtaje(telemetrija, vozac)
    nacrtaj_mapu_staze_po_brzini(telemetrija, vozac)

    return True


def main():
    ukljuci_cache()
    prikazi_naslov()

    sezona = unesi_sezonu()

    kalendar = prikazi_trke_u_sezoni(sezona)

    if kalendar is None:
        return

    broj_trke = izaberi_trku(kalendar)
    tip_sesije = izaberi_tip_sesije()

    sesija = ucitaj_sesiju(sezona, broj_trke, tip_sesije)

    if sesija is None:
        return

    prikazi_vozace(sesija)

    vozac = izaberi_vozaca(sesija)


def korisnik_zeli_drugog_vozaca():
    while True:
        izbor = input("\nDa li želiš da probaš drugog vozača iz iste sesije? da/ne: ").lower()

        if izbor == "da":
            return True
        elif izbor == "ne":
            return False
        else:
            print("Unesi 'da' ili 'ne'.")


def main():
    ukljuci_cache()
    prikazi_naslov()

    sezona = unesi_sezonu()

    kalendar = prikazi_trke_u_sezoni(sezona)

    if kalendar is None:
        return

    broj_trke = izaberi_trku(kalendar)
    tip_sesije = izaberi_tip_sesije()

    sesija = ucitaj_sesiju(sezona, broj_trke, tip_sesije)

    if sesija is None:
        return

    prikazi_vozace(sesija)

    while True:
        vozac = izaberi_vozaca(sesija)

        analiza_uspesna = analiziraj_vozaca(sesija, vozac)

        if analiza_uspesna:
            break

        if not korisnik_zeli_drugog_vozaca():
            print("Analiza je prekinuta.")
            break


if __name__ == "__main__":
    main()