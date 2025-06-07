import pandas as pd

class ExcelVehicleDataRepository:
    def __init__(self, ev_path: str, env_path: str):
        # 1. EV data (tran_r_elvehst...)
        self.ev_data = pd.read_excel(ev_path, sheet_name="Sheet 3", skiprows=9, engine="openpyxl")

        self.records = []
        year_columns_ev = {
            "Unnamed: 1": 2018,
            "Unnamed: 2": 2019,
            "Unnamed: 3": 2020,
            "Unnamed: 4": 2021,
            "Unnamed: 5": 2022
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
        self.env_data = pd.read_excel(env_path, sheet_name="Sheet 1", skiprows=9, engine="openpyxl")

        self.env_records = []
        year_columns_env = {
            "Unnamed: 1": 2013,
            "Unnamed: 2": 2014,
            "Unnamed: 3": 2015,
            "Unnamed: 4": 2016,
            "Unnamed: 5": 2017,
            "Unnamed: 6": 2018,
            "Unnamed: 7": 2019,
            "Unnamed: 8": 2020,
            "Unnamed: 9": 2021,
            "Unnamed: 10": 2022
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
