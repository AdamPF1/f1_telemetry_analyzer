import os
import fastf1

class F1Analyzer:
    def __init__(self, sezona,brojTrka, tipSesije):
        self.seozna = sezona
        self.brojTrka = brojTrka
        self.tipSesije = tipSesije
        self.cache_folder = "cache"

        self._ukluciCache()
        self.sesija = self._ucitajSesiju()

    def _ukljuci_cache(self):
        if not os.path.exists(self, cache_folder):
            os.makedirs(self.cache_folder)
        fastf1.Cache.enable_cache(self.cache_folder)