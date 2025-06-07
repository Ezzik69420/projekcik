from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt

class CountryListWidget(QWidget):
    countriesSelected = pyqtSignal(list)

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.country_names = self.service.get_country_names()

        layout = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Szukaj kraju lub skrótu...")
        self.search_box.textChanged[str].connect(self.filter_list)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.list_widget.itemSelectionChanged.connect(self.emit_selection)

        layout.addWidget(self.search_box)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        self.populate_list()

    def populate_list(self):
        self.list_widget.clear()
        for code in self.service.get_countries():
            full_name = self.country_names.get(code, code)
            display_text = f"{full_name} ({code})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, code)
            self.list_widget.addItem(item)

    def filter_list(self, text):
        text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            visible = text in item.text().lower()
            item.setHidden(not visible)

    def emit_selection(self):
        selected = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.list_widget.selectedItems()
        ]
        self.countriesSelected.emit(selected)

    def get_selected_country_codes(self):
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.list_widget.selectedItems()
        ]
