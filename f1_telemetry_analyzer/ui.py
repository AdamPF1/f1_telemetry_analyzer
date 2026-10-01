from typing import Any, ClassVar


class UI:
    COLORS: ClassVar[dict[str, str]] = {
        "red": "\033[91m",
        "green": "\033[92m",
        "cyan": "\033[96m",
        "yellow": "\033[93m",
        "reset": "\033[0m",
    }
    SESSION_NAMES: ClassVar[dict[str, str]] = {
        "R": "Trka",
        "Q": "Kvalifikacije",
        "FP1": "Prvi trening",
        "FP2": "Drugi trening",
        "FP3": "Treći trening",
        "S": "Sprint",
        "SQ": "Sprint kvalifikacije",
    }

    def header(self) -> None:
        cyan = self.COLORS["cyan"]
        reset = self.COLORS["reset"]
        print(f"\n{cyan}{'═' * 64}{reset}")
        print(f"{cyan}              F1 TELEMETRY ANALYZER{reset}")
        print(f"{cyan}{'═' * 64}{reset}")
        print("Analiza najbržeg kruga na osnovu stvarnih Formula 1 podataka.\n")

    def success(self, message: str) -> None:
        print(f"{self.COLORS['green']}✓ {message}{self.COLORS['reset']}")

    def error(self, message: str) -> None:
        print(f"{self.COLORS['red']}✗ {message}{self.COLORS['reset']}")

    def section(self, title: str) -> str:
        return f"── {title} " + "─" * max(0, 54 - len(title))

    def ask_yes_no(self, message: str) -> bool:
        while True:
            answer = input(f"{message} [da/ne]: ").strip().lower()
            if answer in {"da", "d"}:
                return True
            if answer in {"ne", "n"}:
                return False
            self.error("Unesite 'da' ili 'ne'.")

    def season(self, minimum: int) -> int:
        while True:
            try:
                season = int(input(f"Sezona (preporučeno {minimum}+): "))
            except ValueError:
                self.error("Sezona mora biti ceo broj, na primer 2024.")
                continue
            if season < minimum:
                print(
                    f"{self.COLORS['yellow']}Napomena: starije sezone "
                    f"mogu imati manje podataka.{self.COLORS['reset']}"
                )
            return season

    def race(self, schedule: Any) -> int:
        print(f"\n{self.section('KALENDAR SEZONE')}")
        valid_rounds = set()
        for _, event in schedule.iterrows():
            round_number = int(event["RoundNumber"])
            if round_number == 0:
                continue
            valid_rounds.add(round_number)
            print(f"{round_number:>2}. {event['EventName']} — {event['Location']}")

        while True:
            try:
                race_number = int(input("\nBroj trke: "))
            except ValueError:
                self.error("Broj trke mora biti ceo broj.")
                continue
            if race_number in valid_rounds:
                return race_number
            self.error("Trka sa tim brojem ne postoji u kalendaru.")

    def session_type(self) -> str:
        print(f"\n{self.section('TIP SESIJE')}")
        print("  ".join(f"{key}: {name}" for key, name in self.SESSION_NAMES.items()))
        while True:
            session_type = input("\nTip sesije: ").strip().upper()
            if session_type in self.SESSION_NAMES:
                return session_type
            self.error("Nepoznat tip sesije.")

    def show_drivers(self, session: Any) -> None:
        print(f"\n{self.section('DOSTUPNI VOZAČI')}")
        results = session.results
        if results is not None and not results.empty:
            for _, driver in results.iterrows():
                print(
                    f"{driver['Abbreviation']:<5} "
                    f"{driver['FullName']} — {driver['TeamName']}"
                )
            return
        drivers = sorted(session.laps["Driver"].dropna().unique())
        print(", ".join(drivers))

    def driver(self, session: Any, prompt: str = "Vozač") -> str:
        available = set(session.laps["Driver"].dropna().unique())
        while True:
            driver = input(f"\n{prompt} (npr. VER, HAM, LEC): ").strip().upper()
            if driver in available:
                return driver
            self.error("Vozač nije pronađen u izabranoj sesiji.")

    def loading_error(self, error: Exception) -> None:
        self.error("Podaci nisu mogli da se učitaju.")
        print("Proverite internet, sezonu i dostupnost izabrane sesije.")
        print(f"Detalji: {error}")
