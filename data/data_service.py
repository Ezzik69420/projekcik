# data/data_service.py

from PyQt5.QtCore import QObject, pyqtSignal

class VehicleDataService(QObject):
    dataUpdated = pyqtSignal()
    yearChanged = pyqtSignal(int)

    def __init__(self, repository):
        super().__init__()
        self.repository = repository
        self.selected_year = None
        self.data_mode = "TOTAL"  # lub "EV"

    def set_year(self, year):
        self.selected_year = year
        self.yearChanged.emit(year)
        self.dataUpdated.emit()

    def get_current_year(self):
        return self.selected_year

    def set_mode(self, mode):
        if mode not in {"TOTAL", "EV"}:
            raise ValueError(f"Nieobsługiwany tryb danych: {mode}")
        self.data_mode = mode
        self.dataUpdated.emit()

    def get_countries(self):
        return self.repository.get_all_countries()

    def get_years(self):
        return self.repository.get_available_years()

    def get_data_for_country(self, country):
        if self.selected_year is None:
            return None

        if self.data_mode == "TOTAL":
            # Repository zwraca skumulowaną sumę dla TOTAL
            return self.repository.get_vehicle_data(country, self.selected_year)
        elif self.data_mode == "EV":
            # Sumujemy EV od najwcześniejszego roku do selected_year
            years = self.repository.get_available_years()
            years_to_sum = [y for y in years if y <= self.selected_year]
            total_ev = 0
            for y in years_to_sum:
                val = self.repository.get_ev_share_data(country, y)
                if val is not None:
                    total_ev += val
            return total_ev

        return None

    def get_bulk_data(self, countries):
        return {
            country: self.get_data_for_country(country)
            for country in countries
        }

    def get_country_names(self):
        return {
            "AT": "Austria",
            "BA": "Bośnia i Hercegowina",
            "BE": "Belgia",
            "BG": "Bułgaria",
            "CH": "Szwajcaria",
            "CY": "Cypr",
            "CZ": "Czechy",
            "DE": "Niemcy",
            "DK": "Dania",
            "EE": "Estonia",
            "EL": "Grecja",
            "ES": "Hiszpania",
            "FI": "Finlandia",
            "FR": "Francja",
            "HR": "Chorwacja",
            "HU": "Węgry",
            "IE": "Irlandia",
            "IS": "Islandia",
            "IT": "Włochy",
            "LI": "Liechtenstein",
            "LT": "Litwa",
            "LU": "Luksemburg",
            "LV": "Łotwa",
            "MT": "Malta",
            "NL": "Holandia",
            "NO": "Norwegia",
            "PL": "Polska",
            "PT": "Portugalia",
            "RO": "Rumunia",
            "SE": "Szwecja",
            "SI": "Słowenia",
            "SK": "Słowacja",
            "UK": "Wielka Brytania",
            # Dodaj pozostałe kody, jeżeli się pojawiają w danych:
            # "X1": "Nazwa Kraju X1", itd.
        }