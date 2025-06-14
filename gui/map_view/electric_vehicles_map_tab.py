from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.io as pio
import json
import tempfile
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
from gui.region_switch.region_switch import RegionSwitch

class ElectricVehiclesMapTab(QWidget):
    def __init__(self, data_path: str):
        super().__init__()

        self.ev_data = self.load_ev_data(data_path)
        self.years = sorted(self.ev_data["year"].unique())
        self.start_year = self.years[0]
        self.end_year = self.years[-1]
        self.map_data = self.load_map_data()
        self._complete_ev_data()
        self.region_mode = "EU"
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.region_switch = RegionSwitch(self.on_region_changed)
        self.layout.addWidget(self.region_switch)

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

        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(1200, 800)
        self.layout.addWidget(self.web_view)

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

    def on_region_changed(self, mode: str):
        self.region_mode = mode
        self.render_map()

    def load_ev_data(self, data_path: str) -> pd.DataFrame:

        df_raw = (
            pd.read_excel(
                data_path,
                sheet_name="Sheet 4",                   
                skiprows=8,
                engine="openpyxl",
            )
            .iloc[1:]
        )
        year_columns = {
            "2018": 2018,
            "2019": 2019,
            "2020": 2020,
            "2021": 2021,
            "2022": 2022,
        }
        records = []
        for _, row in df_raw.iterrows():
            geo = str(row["TIME"]).strip()
            name = str(row["TIME.1"]).strip()
                                                                        
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
        gdf = gpd.read_file("data/NUTS_RG_01M_2021_4326.geojson")
        gdf = gdf[gdf["LEVL_CODE"] == 2]         
        gdf = gdf[["NUTS_ID", "geometry"]].copy()
        return gdf.rename(columns={"NUTS_ID": "geo"})

    def _complete_ev_data(self) -> None:
        nuts1_to_nuts2 = {}
        for geo in self.map_data["geo"]:
            prefix = geo[:3] if not geo.startswith("FRY") else "FRY"
            nuts1_to_nuts2.setdefault(prefix, set()).add(geo)

        new_rows = []
        df = self.ev_data
        for prefix, group in df[df["geo"].str.len() == 3].groupby("geo"):
            if prefix in nuts1_to_nuts2:
                has_nuts2 = any(df["geo"].str.startswith(prefix) & (df["geo"].str.len() == 4))
                if not has_nuts2:
                    for _, row in group.iterrows():
                        for geo in nuts1_to_nuts2[prefix]:
                            new_rows.append({
                                "geo": geo,
                                "name": row["name"],
                                "year": row["year"],
                                "value": row["value"],
                            })

        if new_rows:
            self.ev_data = pd.concat([self.ev_data, pd.DataFrame(new_rows)], ignore_index=True)
                            
        self.ev_data = self.ev_data[self.ev_data["geo"].str.len() == 4]

    def render_map(self):
        df_range = self.ev_data[
            (self.ev_data["year"] >= self.start_year) &
            (self.ev_data["year"] <= self.end_year)
        ]

        avg_share = (
            df_range
            .groupby("geo", as_index=False)["value"]
            .mean()
            .rename(columns={"value": "avg_share"})
        )
        region_names = df_range[["geo", "name"]].drop_duplicates(subset="geo")
        avg_share = avg_share.merge(region_names, on="geo", how="left")

        merged = self.map_data.merge(avg_share, on="geo", how="left")
        if self.region_mode == "PL":
            merged = merged[merged["geo"].str.startswith("PL")]
        merged = merged[merged["avg_share"].notna()]

        if merged.empty or merged.geometry.isnull().all():
            return

        geojson = json.loads(merged.to_json())
        fig = go.Figure(go.Choropleth(
            geojson=geojson,
            locations=merged["geo"],
            z=merged["avg_share"],
            featureidkey="properties.geo",
            text=merged["name"],
            colorscale="Viridis",
            marker_line_width=0.5,
            colorbar=dict(
                title=f"Średni udział ({self.start_year}–{self.end_year})",
                x=1.02,
                len=0.75,
                thickness=15,
                ticksuffix="%"
            )
        ))
        fig.update_traces(hovertemplate="%{text}<br>%{z}%<extra></extra>")

        if self.region_mode == "PL":
            minx, miny, maxx, maxy = merged.geometry.total_bounds
            margin = 1
            lat_range = [miny - margin, maxy + margin]
            lon_range = [minx - margin, maxx + margin]
            fig.update_geos(
                projection_type="mercator",
                fitbounds="locations",
                lataxis_range=lat_range,
                lonaxis_range=lon_range,
                visible=True
            )
        else:
            fig.update_geos(
                projection_type="mercator",
                fitbounds="locations",
                lataxis_range=[34, 72],
                lonaxis_range=[-25, 45],
                visible=True
            )
        title_region = "Polska" if self.region_mode == "PL" else "Regiony NUTS2"
        fig.update_layout(
            title=f"Udział pojazdów elektrycznych – {title_region} ({self.start_year}–{self.end_year})",
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            height=800,
            width=1200
        )
        html_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        pio.write_html(fig, file=html_file.name, full_html=True, include_plotlyjs="cdn")
        self.web_view.load(QUrl.fromLocalFile(html_file.name))
