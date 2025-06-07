from PyQt5.QtWidgets import QApplication
from common.config import Config
from data.repository import ExcelVehicleDataRepository
from data.data_service import VehicleDataService
from export.pdf_exporter import PDFExportStrategy
from gui.main_window.main_window import MainWindow
import sys, os
def main():
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
    os.environ["QT_QUICK_BACKEND"] = "software"
    app = QApplication(sys.argv)
    config = Config()
    repository = ExcelVehicleDataRepository(config.ev_data_path, config.env_data_path)
    service = VehicleDataService(repository)
    exporter = PDFExportStrategy()
    window = MainWindow(service, exporter)
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()
