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
        self.repo_df = self.service.repository.df.copy()
        self.years = sorted(self.repo_df["TIME_PERIOD"].unique())
        self.start_year = self.years[0]
        self.end_year = self.years[-1]
        self.selected_countries = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        sliders_layout = QHBoxLayout()

        self.label_start = QLabel(f"Od roku: {self.start_year}")
        self.slider_start = QSlider(Qt.Horizontal)
        self.slider_start.setMinimum(0)
        self.slider_start.setMaximum(len(self.years) - 1)
        self.slider_start.setValue(0)
        self.slider_start.setTickInterval(1)
        self.slider_start.setTickPosition(QSlider.TicksBelow)
        self.slider_start.valueChanged.connect(self.on_start_changed)

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
        self.country_list_widget = CountryListWidget(self.service)
        self.country_list_widget.countriesSelected.connect(self.update_countries)
        self.layout.addWidget(self.country_list_widget)
        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.service.dataUpdated.connect(self.redraw_chart)
        self.redraw_chart()

    def on_start_changed(self, index: int):

        year = self.years[index]
        if year > self.end_year:
            self.slider_end.setValue(index)
            return
        self.start_year = year
        self.label_start.setText(f"Od roku: {self.start_year}")
        self.redraw_chart()

    def on_end_changed(self, index: int):

        year = self.years[index]
        if year < self.start_year:
            self.slider_start.setValue(index)
            return
        self.end_year = year
        self.label_end.setText(f"Do roku: {self.end_year}")
        self.redraw_chart()

    def update_countries(self, countries: list):

        self.selected_countries = countries
        self.redraw_chart()

    def redraw_chart(self):

        try:

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

            mask = (
                (self.repo_df["TIME_PERIOD"] >= self.start_year) &
                (self.repo_df["TIME_PERIOD"] <= self.end_year) &
                (self.repo_df["geo"].isin(self.selected_countries))
            )
            df_range = self.repo_df[mask]

            cum_df = (
                df_range
                .groupby("geo", as_index=False)["OBS_VALUE"]
                .sum()
                .rename(columns={"OBS_VALUE": "cumulative_value"})
            )
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

            missing = set(self.selected_countries) - set(cum_df["geo"])
            if missing:
                rows = [{"geo": geo_code, "cumulative_value": 0} for geo_code in missing]
                missing_df = pd.DataFrame(rows, columns=["geo", "cumulative_value"])
                cum_df = pd.concat([cum_df, missing_df], ignore_index=True)

            cum_df = cum_df.sort_values("geo")
            country_codes = cum_df["geo"].tolist()

            values = []
            for x in cum_df["cumulative_value"].tolist():
                try:
                    f = float(x)
                except Exception:
                    f = 0.0
                values.append(f)

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
            ax.set_ylabel("Liczba ENV")
            ax.tick_params(axis='x', labelrotation=45)
            ax.ticklabel_format(style='plain', axis='y')

            self.figure.subplots_adjust(bottom=0.28)

            country_names_dict = self.service.get_country_names()
            legend_entries = [
                f"{code} – {country_names_dict.get(code, code)}"
                for code in country_codes
            ]
            n_per_row = 4
            lines = [
                ", ".join(legend_entries[i:i + n_per_row])
                for i in range(0, len(legend_entries), n_per_row)
            ]
            legend_text = "\n".join(lines)

            self.figure.text(
                0.5, 0.08,                                                      
                legend_text,
                ha='center',
                va='top',
                fontsize=8
            )
            self.canvas.draw()
        except Exception as e:
            print(f"❌ Błąd w redraw_chart(): {e}")
