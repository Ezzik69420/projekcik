# gui/map_view/electric_vehicles_countries_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.io as pio
import json
import tempfile

class ElectricVehiclesCountriesTab(QWidget):
    def __init__(self, data_path: str):
        super().__init__()

        self.country_name_to_code = {
            "Germany": "DE",
            "France": "FR",
            "Italy": "IT",
            "Spain": "ES",
            "Poland": "PL",
            "Netherlands": "NL",
            "Belgium": "BE",
            "Sweden": "SE",
            "Finland": "FI",
            "Austria": "AT",
            "Portugal": "PT",
            "Czechia": "CZ",
            "Denmark": "DK",
            "Greece": "EL",
            "Hungary": "HU",
            "Ireland": "IE",
            "Slovakia": "SK",
            "Slovenia": "SI",
            "Croatia": "HR",
            "Estonia": "EE",
            "Latvia": "LV",
            "Lithuania": "LT",
            "Luxembourg": "LU",
            "Bulgaria": "BG",
            "Romania": "RO",
            "Norway": "NO",
            "Switzerland": "CH",
            "Iceland": "IS",
            "Cyprus": "CY",
        }

        # 1) Wczytujemy dane EV z Excela i dostępne lata
        self.env_data = self.load_env_data(data_path)
        self.years = sorted(self.env_data["year"].unique())
        self.start_year = self.years[0]
        self.end_year = self.years[-1]

        # 2) Wczytujemy geometrię krajów (poziom 0)
        self.map_data = self.load_map_data()

        # ------------------------
        # Przygotowanie interfejsu Qt
        # ------------------------
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Suwaki „Od roku” / „Do roku” ---
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

        # --- Widok mapy w HTML ---
        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(1200, 800)
        self.layout.addWidget(self.web_view)

        # Rysujemy mapę od razu
        self.render_map()

    def on_start_changed(self, index: int):
        year = self.years[index]
        if year > self.end_year:
            self.slider_end.setValue(index)
            return
        self.start_year = year
        self.label_start.setText(f"Od roku: {self.start_year}")
        self.render_map()

    def on_end_changed(self, index: int):
        year = self.years[index]
        if year < self.start_year:
            self.slider_start.setValue(index)
            return
        self.end_year = year
        self.label_end.setText(f"Do roku: {self.end_year}")
        self.render_map()

    def load_env_data(self, data_path: str) -> pd.DataFrame:
        """
        Wczytuje plik Excel z danymi ENV.
        Pierwszych osiem wierszy zawiera opis, kolejne wiersze zaczynają się od
        kolumny "TIME" z nazwą kraju oraz kolumn z latami (2013–2022). Pierwszy
        wiersz po nagłówku powtarza opisy i jest pomijany.
        Zwraca DataFrame z kolumnami: ``geo``, ``name``, ``year`` i ``value``.
        """
        df_raw = (
            pd.read_excel(
                data_path,
                sheet_name="Sheet 1",
                skiprows=8,
                engine="openpyxl",
            )
            .iloc[1:]
        )

        year_columns = {
            "2013": 2013,
            "2014": 2014,
            "2015": 2015,
            "2016": 2016,
            "2017": 2017,
            "2018": 2018,
            "2019": 2019,
            "2020": 2020,
            "2021": 2021,
            "2022": 2022,
        }

        records = []
        for _, row in df_raw.iterrows():
            name = str(row.get("TIME", "")).strip()
            geo = self.country_name_to_code.get(name)
            if not geo:
                continue
            for col_name, rok in year_columns.items():
                val = row.get(col_name)
                if pd.notna(val) and isinstance(val, (int, float)):
                    records.append({
                        "geo": geo,
                        "name": name,
                        "year": rok,
                        "value": val
                    })
        return pd.DataFrame(records)

    def load_map_data(self) -> gpd.GeoDataFrame:
        """
        Wczytuje geojson z krajami (poziom 0 NUTS).
        Plik: 'data/NUTS_RG_01M_2021_4326.geojson'.
        """
        gdf = gpd.read_file("data/NUTS_RG_01M_2021_4326.geojson")
        gdf = gdf[gdf["LEVL_CODE"] == 0]
        gdf = gdf[["CNTR_CODE", "NAME_LATN", "geometry"]].copy()
        return gdf.rename(columns={"CNTR_CODE": "geo", "NAME_LATN": "name"})

    def render_map(self):
        # 1) filtrujemy EV w zakresie [start_year, end_year]
        df_range = self.env_data[
            (self.env_data["year"] >= self.start_year) &
            (self.env_data["year"] <= self.end_year)
        ]

        # 2) grupujemy po 'geo' i sumujemy 'value'
        cum_env = (
            df_range
            .groupby("geo", as_index=False)["value"]
            .sum()
            .rename(columns={"value": "cumulative_env"})
        )

        # 3) łączymy z geometrią krajów
        merged = self.map_data.merge(cum_env, on="geo", how="left")
        merged = merged[merged["cumulative_env"].notna()]

        if merged.empty or merged.geometry.isnull().all():
            return

        # 4) rysujemy choropleth
        geojson = json.loads(merged.to_json())
        fig = go.Figure(go.Choropleth(
            geojson=geojson,
            locations=merged["geo"],
            z=merged["cumulative_env"],
            featureidkey="properties.geo",
            text=merged["name"],
            colorscale="RdPu",
            marker_line_width=0.5,
            colorbar=dict(
                title=f"Suma ENV ({self.start_year}–{self.end_year})",
                x=1.02,
                len=0.75,
                thickness=15
            )
        ))
        fig.update_traces(hovertemplate="%{text}<br>%{z}<extra></extra>")

        fig.update_geos(
            projection_type="mercator",
            fitbounds="locations",
            lataxis_range=[34, 72],
            lonaxis_range=[-25, 45],
            visible=True
        )

        fig.update_layout(
            title=f"Pojazdy elektryczne – Europa ({self.start_year}–{self.end_year})",
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            height=800,
            width=1200
        )

        html_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        pio.write_html(fig, file=html_file.name, full_html=True, include_plotlyjs="cdn")
        self.web_view.load(QUrl.fromLocalFile(html_file.name))