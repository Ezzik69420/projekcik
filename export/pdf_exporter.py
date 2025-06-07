
from matplotlib.backends.backend_pdf import PdfPages

class PDFExportStrategy:
    def export(self, figure, filename):
        with PdfPages(filename) as pdf:
            pdf.savefig(figure)
