class MainController:
    def __init__(self, service, exporter, chart_view, map_view):
        self.service = service
        self.exporter = exporter
        self.chart_view = chart_view
        self.map_view = map_view
        self.service.dataUpdated.connect(self.update_views)
    def on_year_changed(self, year):
        self.service.set_year(year)
    def on_mode_changed(self, mode):
        self.service.set_mode(mode)
    def on_export_clicked(self, filename):
        if self.chart_view.figure:
            self.exporter.export(self.chart_view.figure, filename)
    def update_views(self):
        self.map_view.refresh()
        self.chart_view.refresh()
