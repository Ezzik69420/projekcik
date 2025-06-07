from PyQt5.QtWidgets import QPushButton, QFileDialog
class ExportButton(QPushButton):
    def __init__(self, chart_view, exporter):
        super().__init__("Eksportuj do PDF")
        self.chart_view = chart_view
        self.exporter = exporter
        self.clicked.connect(self.export)
    def export(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Zapisz PDF", "", "PDF files (*.pdf)")
        if file_name:
            self.exporter.export(self.chart_view.figure, file_name)
