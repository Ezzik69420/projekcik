from PyQt5.QtWidgets import QWidget, QHBoxLayout, QRadioButton, QLabel, QButtonGroup
class ModeSwitch(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Tryb danych:"))
        self.group = QButtonGroup(self)
        self.total_btn = QRadioButton("Ogółem")
        self.ev_btn = QRadioButton("Elektryczne")
        self.total_btn.setChecked(True)
        self.group.addButton(self.total_btn)
        self.group.addButton(self.ev_btn)
        self.total_btn.toggled.connect(self.mode_changed)
        layout.addWidget(self.total_btn)
        layout.addWidget(self.ev_btn)
        self.setLayout(layout)
    def mode_changed(self):
        mode = "TOTAL" if self.total_btn.isChecked() else "EV"
        self.service.set_mode(mode)
