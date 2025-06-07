from PyQt5.QtWidgets import QWidget, QHBoxLayout, QRadioButton, QLabel, QButtonGroup

class RegionSwitch(QWidget):
    def __init__(self, callback=None):
        super().__init__()

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Region:"))

        self.group = QButtonGroup(self)
        self.eu_btn = QRadioButton("Europa")
        self.pl_btn = QRadioButton("Polska")
        self.eu_btn.setChecked(True)
        self.group.addButton(self.eu_btn)
        self.group.addButton(self.pl_btn)

        if callback:
            self.eu_btn.toggled.connect(lambda: callback("EU"))
            self.pl_btn.toggled.connect(lambda: callback("PL"))

        layout.addWidget(self.eu_btn)
        layout.addWidget(self.pl_btn)
        self.setLayout(layout)
