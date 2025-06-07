from PyQt5.QtCore import QObject, pyqtSignal
class VehicleDataService(QObject):
    dataUpdated = pyqtSignal()

    def __init__(self, repository):
        super().__init__()
        self.repository = repository
        self.selected_year = None

    def set_year(self, year):
        self.selected_year = year
        self.dataUpdated.emit()

    def get_countries(self):
        return self.repository.get_all_countries()

    def get_years(self):
        return self.repository.get_available_years()


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
                                                                  
                                          
        }
