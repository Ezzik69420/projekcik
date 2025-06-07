# gui/main_window/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QPushButton, QFileDialog
)
from common.config import Config
from gui.map_view.electric_vehicles_map_tab import ElectricVehiclesMapTab
from gui.map_view.electric_vehicles_countries_tab import ElectricVehiclesCountriesTab
from gui.chart_view.chart_view import ChartView  # zmodyfikowana wersja z dwoma suwakami
from gui.country_list_widget.country_list_widget import CountryListWidget

class MainWindow(QMainWindow):
    def __init__(self, service, exporter=None):
        super().__init__()
        self.setWindowTitle("Wizualizacja pojazdów elektrycznych")
        self.setMinimumSize(1200, 800)

        self.service = service
        self.exporter = exporter

        cfg = Config()
        region_csv = cfg.ev_data_path
        country_xlsx = cfg.env_data_path

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_tabs(region_csv, country_xlsx)

    def init_tabs(self, region_csv, country_xlsx):
        print("✅ init_tabs start")

        # ---------------------------------
        # 1) Zakładka „Mapa EV – regiony”
        # ---------------------------------
        try:
            ev_map_widget = QWidget()
            ev_map_layout = QVBoxLayout()

            # ElectricVehiclesMapTab już wewnątrz tworzy dwa suwaki
            self.ev_map_tab = ElectricVehiclesMapTab(region_csv)
            ev_map_layout.addWidget(self.ev_map_tab)

            ev_map_widget.setLayout(ev_map_layout)
            self.tabs.addTab(ev_map_widget, "Mapa EV – regiony")
        except Exception as e:
            print(f"❌ Błąd przy ev_map_tab: {e}")

        # ---------------------------------
        # 2) Zakładka „Mapa EV – kraje”
        # ---------------------------------
        try:
            ev_countries_widget = QWidget()
            ev_countries_layout = QVBoxLayout()

            # ElectricVehiclesCountriesTab również tworzy dwa suwaki
            self.ev_countries_tab = ElectricVehiclesCountriesTab(country_xlsx)
            ev_countries_layout.addWidget(self.ev_countries_tab)

            ev_countries_widget.setLayout(ev_countries_layout)
            self.tabs.addTab(ev_countries_widget, "Mapa EV – kraje")
        except Exception as e:
            print(f"❌ Błąd przy ev_countries_tab: {e}")

        # ---------------------------------
        # 3) Zakładka „Porównanie krajów”
        # ---------------------------------
        try:
            chart_tab = QWidget()
            layout = QVBoxLayout()

            # ChartView zmieniony tak, aby miał dwa suwaki
            self.chart_view = ChartView(self.service)
            # Na razie CountryListWidget umieszczamy wewnątrz ChartView,
            # bo to wygodniej (zobacz ChartView.py).

            layout.addWidget(self.chart_view)

            if self.exporter:
                export_button = QPushButton("Eksportuj wykres do PDF")
                export_button.clicked.connect(self.export_pdf)
                layout.addWidget(export_button)

            chart_tab.setLayout(layout)
            self.tabs.addTab(chart_tab, "Porównanie krajów")
        except Exception as e:
            print(f"❌ Błąd przy chart_tab: {e}")

    def export_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Zapisz PDF", "", "PDF files (*.pdf)")
        if file_name:
            self.exporter.export(self.chart_view.figure, file_name)