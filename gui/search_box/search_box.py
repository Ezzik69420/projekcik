from PyQt5.QtWidgets import QLineEdit
class SearchBox(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Wyszukaj kraj...")

