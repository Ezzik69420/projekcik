import pandas as pd

class ExcelVehicleDataRepository:
    def __init__(self, ev_path: str, env_path: str):
                                        
                                                                             
                                                                             
                                                              
        ev_raw = pd.read_excel(
            ev_path,
            sheet_name="Sheet 3",
            skiprows=8,
            engine="openpyxl",
        )
        ev_raw = ev_raw.rename(
            columns={
                "TIME": "GEO (Codes)",
                "TIME.1": "GEO (Labels)",
                "Unnamed: 3": "_drop1",
                "Unnamed: 5": "_drop2",
                "Unnamed: 7": "_drop3",
                "Unnamed: 9": "_drop4",
                "Unnamed: 11": "_drop5",
            }
        )
        ev_raw = ev_raw.drop(columns=["_drop1", "_drop2", "_drop3", "_drop4", "_drop5"])\
            .iloc[1:]
        self.ev_data = ev_raw
        self.name_to_code = {
            str(row["GEO (Labels)"]).strip(): str(row["GEO (Codes)"]).strip()
            for _, row in self.ev_data.iterrows()
            if len(str(row["GEO (Codes)"]).strip()) == 2
        }

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

                                      
                                                                           
                                                                         
        env_raw = pd.read_excel(
            env_path,
            sheet_name="Sheet 1",
            skiprows=8,
            engine="openpyxl",
        )
        env_raw = env_raw.rename(
            columns={
                "TIME": "GEO (Labels)",
                "Unnamed: 2": "_drop1",
                "Unnamed: 4": "_drop2",
                "Unnamed: 6": "_drop3",
                "Unnamed: 8": "_drop4",
                "Unnamed: 10": "_drop5",
                "Unnamed: 12": "_drop6",
                "Unnamed: 14": "_drop7",
                "Unnamed: 16": "_drop8",
                "Unnamed: 18": "_drop9",
                "Unnamed: 20": "_drop10",
            }
        )
        env_raw = env_raw.drop(columns=[
            "_drop1",
            "_drop2",
            "_drop3",
            "_drop4",
            "_drop5",
            "_drop6",
            "_drop7",
            "_drop8",
            "_drop9",
            "_drop10",
        ]).iloc[1:]
        self.env_data = env_raw

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
            label = str(row["GEO (Labels)"]).strip()
            geo = self.name_to_code.get(label)
            if geo:
                for col_name, year in year_columns_env.items():
                    val = row.get(col_name)
                    if pd.notna(val):
                        try:
                            numeric_val = float(val)
                            self.env_records.append({
                                "geo": geo,
                                "TIME_PERIOD": year,
                                "OBS_VALUE": numeric_val,
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
