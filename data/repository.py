import pandas as pd

class ExcelVehicleDataRepository:
    def __init__(self, ev_path: str, env_path: str):
        # 1. EV data (tran_r_elvehst...)
        # Wczytujemy dane EV. W arkuszu po ośmiu wierszach znajdują się nazwy
        # kolumn z latami (2018, 2019, ...). Kolejny wiersz powtarza nagłówki
        # "GEO (Codes)", dlatego pomijamy go przy wczytywaniu.
        self.ev_data = pd.read_excel(
            ev_path,
            sheet_name="Sheet 3",
            skiprows=8,
            engine="openpyxl",
        )
        self.ev_data.rename(
            columns={"TIME": "GEO (Codes)", "TIME.1": "GEO (Labels)"},
            inplace=True,
        )
        self.ev_data = self.ev_data.iloc[1:]

        self.records = []
        year_columns_ev = {
            "2018": 2018,
            "2019": 2019,
            "2020": 2020,
            "2021": 2021,
            "2022": 2022,
        }

        for _, row in self.ev_data.iterrows():
            geo = str(row["GEO (Codes)"]).strip()
            name = str(row["GEO (Labels)"]).strip()
            if len(geo) == 2:
                for col_name, year in year_columns_ev.items():
                    val = row.get(col_name)
                    if pd.notna(val):
                        try:
                            numeric_val = float(val)
                            self.records.append({
                                "geo": geo,
                                "TIME_PERIOD": year,
                                "OBS_VALUE": numeric_val
                            })
                        except Exception:
                            continue

        self.df = pd.DataFrame(self.records)

        # 2. ENV data (env_waselvt...)
        # Dane ENV mają podobną strukturę – po ośmiu wierszach znajdują się
        # kolumny z latami, a pierwszy wiersz po nagłówku należy pominąć.
        self.env_data = pd.read_excel(
            env_path,
            sheet_name="Sheet 1",
            skiprows=8,
            engine="openpyxl",
        )
        self.env_data.rename(columns={"TIME": "GEO (Labels)"}, inplace=True)
        self.env_data = self.env_data.iloc[1:]

        self.env_records = []
        year_columns_env = {
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

        for _, row in self.env_data.iterrows():
            geo = str(row["GEO (Labels)"]).strip()
            if len(geo) == 2:
                for col_name, year in year_columns_env.items():
                    val = row.get(col_name)
                    if pd.notna(val):
                        try:
                            numeric_val = float(val)
                            self.env_records.append({
                                "geo": geo,
                                "TIME_PERIOD": year,
                                "OBS_VALUE": numeric_val
                            })
                        except Exception:
                            continue

        self.env_df = pd.DataFrame(self.env_records)

    def get_all_countries(self):
        countries = self.df["geo"].dropna().unique()
        return sorted(set(countries))

    def get_available_years(self):
        return sorted(self.df["TIME_PERIOD"].unique())

    def get_vehicle_data(self, country: str, year: int):
        return self.get_ev_share_data(country, year)

    def get_ev_share_data(self, country: str, year: int):
        row = self.df[(self.df["geo"] == country) & (self.df["TIME_PERIOD"] == year)]
        if not row.empty:
            return row.iloc[0]["OBS_VALUE"]
        return None

    def get_env_data(self, country: str, year: int):
        row = self.env_df[(self.env_df["geo"] == country) & (self.env_df["TIME_PERIOD"] == year)]
        if not row.empty:
            return row.iloc[0]["OBS_VALUE"]
        return None
