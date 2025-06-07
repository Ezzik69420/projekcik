from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
class YearSlider(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.layout = QHBoxLayout()
        self.label = QLabel("Rok: ")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        years = self.service.get_years()
        if years:
            self.years = sorted(years)
            self.slider.setMinimum(0)
            self.slider.setMaximum(len(self.years) - 1)
            default_year = 2022 if 2022 in self.years else self.years[0]
            default_index = self.years.index(default_year)
            self.slider.setValue(default_index)
            self.label.setText(f"Rok: {default_year}")
            self.service.set_year(default_year)
            self.slider.valueChanged.connect(self.update_year)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider)
        self.setLayout(self.layout)
    def update_year(self, index):
        year = self.years[index]
        self.label.setText(f"Rok: {year}")
        self.service.set_year(year)
