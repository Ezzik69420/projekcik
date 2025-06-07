class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.env_data_path = "env_waselvt$defaultview_spreadsheet.xlsx"
        self.ev_data_path = "tran_r_elvehst$defaultview_spreadsheet.xlsx"
