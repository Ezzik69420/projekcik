# gui/chart_view/ChartView.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from gui.country_list_widget.country_list_widget import CountryListWidget

import matplotlib.pyplot as plt
import pandas as pd


class ChartView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service

        # -------------------------------------------------------
        # 1) Pobieramy pełny DataFrame z repozytorium:
        #    kolumny: ["geo", "TIME_PERIOD", "OBS_VALUE"]
        # -------------------------------------------------------
        self.repo_df = self.service.repository.df.copy()

        # -------------------------------------------------------
        # 2) Wyciągamy unikalne lata i ustawiamy domyślny zakres:
        #    od pierwszego do ostatniego roku.
        # -------------------------------------------------------
        self.years = sorted(self.repo_df["TIME_PERIOD"].unique())
        self.start_year = self.years[0]
        self.end_year = self.years[-1]

        # -------------------------------------------------------
        # 3) Lista aktualnie zaznaczonych krajów (na początku pusta)
        # -------------------------------------------------------
        self.selected_countries = []

        # -------------------------------------------------------
        # 4) Budujemy układ Qt: suwaki, lista krajów, miejsce na wykres
        # -------------------------------------------------------
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 4.1) Suwaki „Od roku” / „Do roku”
        sliders_layout = QHBoxLayout()

        # Suwak początkowego roku
        self.label_start = QLabel(f"Od roku: {self.start_year}")
        self.slider_start = QSlider(Qt.Horizontal)
        self.slider_start.setMinimum(0)
        self.slider_start.setMaximum(len(self.years) - 1)
        self.slider_start.setValue(0)
        self.slider_start.setTickInterval(1)
        self.slider_start.setTickPosition(QSlider.TicksBelow)
        self.slider_start.valueChanged.connect(self.on_start_changed)

        # Suwak końcowego roku
        self.label_end = QLabel(f"Do roku: {self.end_year}")
        self.slider_end = QSlider(Qt.Horizontal)
        self.slider_end.setMinimum(0)
        self.slider_end.setMaximum(len(self.years) - 1)
        self.slider_end.setValue(len(self.years) - 1)
        self.slider_end.setTickInterval(1)
        self.slider_end.setTickPosition(QSlider.TicksBelow)
        self.slider_end.valueChanged.connect(self.on_end_changed)

        sliders_layout.addWidget(self.label_start)
        sliders_layout.addWidget(self.slider_start)
        sliders_layout.addSpacing(20)
        sliders_layout.addWidget(self.label_end)
        sliders_layout.addWidget(self.slider_end)
        self.layout.addLayout(sliders_layout)

        # 4.2) Lista krajów (CountryListWidget)
        self.country_list_widget = CountryListWidget(self.service)
        self.country_list_widget.countriesSelected.connect(self.update_countries)
        self.layout.addWidget(self.country_list_widget)

        # 4.3) Miejsce na wykres Matplotlib
        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # -------------------------------------------------------
        # 5) Podłączamy sygnał, by reagować na ewentualną zmianę
        #    (np. tryb EV/TOTAL lub inna aktualizacja danych).
        # -------------------------------------------------------
        self.service.dataUpdated.connect(self.redraw_chart)

        # -------------------------------------------------------
        # 6) Rysujemy wykres po raz pierwszy (np. komunikat o braku krajów).
        # -------------------------------------------------------
        self.redraw_chart()

    def on_start_changed(self, index: int):
        """
        Wywoływane, gdy użytkownik przesunie suwak początkowego roku.
        Jeżeli ustawiony rok > end_year, to również przesuwamy suwak końcowy.
        """
        year = self.years[index]
        if year > self.end_year:
            self.slider_end.setValue(index)
            return
        self.start_year = year
        self.label_start.setText(f"Od roku: {self.start_year}")
        self.redraw_chart()

    def on_end_changed(self, index: int):
        """
        Wywoływane, gdy użytkownik przesunie suwak końcowego roku.
        Jeżeli ustawiony rok < start_year, to również przesuwamy suwak początkowy.
        """
        year = self.years[index]
        if year < self.start_year:
            self.slider_start.setValue(index)
            return
        self.end_year = year
        self.label_end.setText(f"Do roku: {self.end_year}")
        self.redraw_chart()

    def update_countries(self, countries: list):
        """
        Wywoływane, gdy użytkownik zmienia zaznaczone kraje w CountryListWidget.
        Zapisujemy ich listę i odświeżamy wykres.
        """
        self.selected_countries = countries
        self.redraw_chart()

    def redraw_chart(self):
        """
        Tworzy lub odświeża wykres słupkowy według następującej logiki:
        1) Jeżeli nie wybrano żadnego kraju: komunikat „Zaznacz co najmniej jeden kraj”.
        2) Filtrujemy repo_df po wybranym zakresie lat i krajach.
        3) Grupujemy po 'geo' i sumujemy 'OBS_VALUE' → cum_df.
        4) Jeżeli cum_df jest pusty: komunikat „Brak danych w wybranym zakresie lat”.
        5) Dodajemy brakujące kraje (wartość 0) oraz sortujemy alfabetycznie.
        6) Konwertujemy wartości na float.
        7) Rysujemy słupki i etykiety nad nimi.
        8) Pod wykresem wyświetlamy legendę (kod – pełna nazwa).
           Pilnujemy, by legendę umieścić w obszarze figury (subplots_adjust).
        Całość jest owinięta w try/except, aby ewentualne błędy nie zamknęły aplikacji.
        """
        try:
            # -------------------------------------------------------
            # 1) Sprawdzenie: czy wybrano jakiekolwiek kraje?
            # -------------------------------------------------------
            if not self.selected_countries:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(
                    0.5, 0.5,
                    "Zaznacz przynajmniej jeden kraj",
                    ha='center', va='center', fontsize=12
                )
                ax.set_xticks([])
                ax.set_yticks([])
                self.canvas.draw()
                return

            # -------------------------------------------------------
            # 2) Filtrujemy repo_df: TIME_PERIOD ∈ [start_year, end_year],
            #    geo ∈ selected_countries
            # -------------------------------------------------------
            mask = (
                (self.repo_df["TIME_PERIOD"] >= self.start_year) &
                (self.repo_df["TIME_PERIOD"] <= self.end_year) &
                (self.repo_df["geo"].isin(self.selected_countries))
            )
            df_range = self.repo_df[mask]

            # -------------------------------------------------------
            # 3) Grupujemy po 'geo' i sumujemy 'OBS_VALUE'
            # -------------------------------------------------------
            cum_df = (
                df_range
                .groupby("geo", as_index=False)["OBS_VALUE"]
                .sum()
                .rename(columns={"OBS_VALUE": "cumulative_value"})
            )

            # -------------------------------------------------------
            # 4) Jeśli cum_df jest pusty → komunikat i return
            # -------------------------------------------------------
            if cum_df.empty:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(
                    0.5, 0.5,
                    "Brak danych w wybranym zakresie lat",
                    ha='center', va='center', fontsize=12
                )
                ax.set_xticks([])
                ax.set_yticks([])
                self.canvas.draw()
                return

            # -------------------------------------------------------
            # 5) Dodajemy brakujące kraje (wartość 0) → sortujemy alfabetycznie
            # -------------------------------------------------------
            missing = set(self.selected_countries) - set(cum_df["geo"])
            if missing:
                # Tworzymy nowy DataFrame tylko z brakującymi wierszami
                rows = [{"geo": geo_code, "cumulative_value": 0} for geo_code in missing]
                missing_df = pd.DataFrame(rows, columns=["geo", "cumulative_value"])
                cum_df = pd.concat([cum_df, missing_df], ignore_index=True)

            cum_df = cum_df.sort_values("geo")

            country_codes = cum_df["geo"].tolist()

            # -------------------------------------------------------
            # 6) Konwersja wszystkich wartości na float (zabezpieczenie)
            # -------------------------------------------------------
            values = []
            for x in cum_df["cumulative_value"].tolist():
                try:
                    f = float(x)
                except Exception:
                    f = 0.0
                values.append(f)

            # -------------------------------------------------------
            # 7) Rysujemy wykres słupkowy
            # -------------------------------------------------------
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            cmap = plt.get_cmap('tab20', len(values))
            colors = [cmap(i) for i in range(len(values))]

            bars = ax.bar(country_codes, values, color=colors)

            max_val = max(values) if values else 1.0
            max_val = float(max_val)
            ax.set_ylim(0, max_val * 1.2)

            fontsize = 8 if len(values) <= 10 else 6
            for bar, val in zip(bars, values):
                h = float(bar.get_height())
                offset = 0.03 * max_val
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    h + offset,
                    f"{int(val):,}",
                    ha='center', va='bottom',
                    fontsize=fontsize, rotation='vertical'
                )

            ax.set_title(f"Wybrane kraje – suma EV ({self.start_year}–{self.end_year})")
            ax.set_ylabel("Liczba EV")
            ax.tick_params(axis='x', labelrotation=45)
            ax.ticklabel_format(style='plain', axis='y')

            # -------------------------------------------------------
            # 8) Przydzielamy więcej miejsca na dole, żeby zmieścić legendę
            # -------------------------------------------------------
            self.figure.subplots_adjust(bottom=0.28)

            # -------------------------------------------------------
            # 9) Budujemy legendę pod wykresem: kod – pełna nazwa
            # -------------------------------------------------------
            country_names_dict = self.service.get_country_names()
            legend_entries = [
                f"{code} – {country_names_dict.get(code, code)}"
                for code in country_codes
            ]
            # Maksymalnie 4 elementy w jednym wierszu
            n_per_row = 4
            lines = [
                ", ".join(legend_entries[i:i + n_per_row])
                for i in range(0, len(legend_entries), n_per_row)
            ]
            legend_text = "\n".join(lines)

            # Umieszczamy legendę w obszarze figury poniżej osi X:
            self.figure.text(
                0.5, 0.08,  # x=0.5 (środek), y=0.08 (nieco nad dolną krawędzią)
                legend_text,
                ha='center',
                va='top',
                fontsize=8
            )

            # -------------------------------------------------------
            # 10) Rysujemy wszystko na kanwie
            # -------------------------------------------------------
            self.canvas.draw()

        except Exception as e:
            print(f"❌ Błąd w redraw_chart(): {e}")
