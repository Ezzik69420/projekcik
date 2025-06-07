import pandas as pd


class ExcelVehicleDataRepository:
    def __init__(self, ev_path: str, env_path: str):
        # Load raw sheets
        self.ev_data = self._load_ev_sheet(ev_path)
        self.env_data = self._load_env_sheet(env_path)

        # Map full country names to two‑letter codes
        self.name_to_code = {
            row["GEO (Labels)"].strip(): row["GEO (Codes)"].strip()
            for _, row in self.ev_data.iterrows()
            if len(str(row["GEO (Codes)"]).strip()) == 2
        }

        # Prepare final data frames
        self.df = self._extract_records(
            self.ev_data,
            "GEO (Codes)",
            {str(y): y for y in range(2018, 2023)},
        )

        env_years = {str(y): y for y in range(2013, 2023)}
        self.env_data["geo"] = self.env_data["GEO (Labels)"].map(self.name_to_code)
        self.env_df = self._extract_records(self.env_data.dropna(subset=["geo"]), "geo", env_years)

    @staticmethod
    def _load_sheet(path: str, sheet: str, rename: dict) -> pd.DataFrame:
        df = pd.read_excel(path, sheet_name=sheet, skiprows=8, engine="openpyxl").iloc[1:]
        df = df.rename(columns=rename)
        drop_cols = [c for c in rename.values() if c.startswith("_drop")]
        return df.drop(columns=drop_cols)

    def _load_ev_sheet(self, path: str) -> pd.DataFrame:
        rename = {
            "TIME": "GEO (Codes)",
            "TIME.1": "GEO (Labels)",
            **{f"Unnamed: {i}": f"_drop{i//2}" for i in range(3, 12, 2)},
        }
        return self._load_sheet(path, "Sheet 3", rename)

    def _load_env_sheet(self, path: str) -> pd.DataFrame:
        rename = {"TIME": "GEO (Labels)"}
        rename.update({f"Unnamed: {i}": f"_drop{i//2 - 1}" for i in range(2, 21, 2)})
        return self._load_sheet(path, "Sheet 1", rename)

    @staticmethod
    def _extract_records(df: pd.DataFrame, code_col: str, years: dict) -> pd.DataFrame:
        long_df = df.melt(id_vars=[code_col], value_vars=years.keys(), var_name="TIME_PERIOD", value_name="OBS_VALUE")
        long_df["TIME_PERIOD"] = long_df["TIME_PERIOD"].map(years)
        long_df[code_col] = long_df[code_col].astype(str).str.strip()
        long_df = long_df.dropna(subset=["OBS_VALUE"])
        long_df["OBS_VALUE"] = pd.to_numeric(long_df["OBS_VALUE"], errors="coerce")
        long_df = long_df.dropna(subset=["OBS_VALUE"])
        long_df.rename(columns={code_col: "geo"}, inplace=True)
        return long_df[["geo", "TIME_PERIOD", "OBS_VALUE"]]

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

