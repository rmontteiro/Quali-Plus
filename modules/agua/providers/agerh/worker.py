# -*- coding: utf-8 -*-
"""
Worker assíncrono para execução do provedor AGERH sem bloqueio do QGIS.
"""

from qgis.PyQt.QtCore import QThread, pyqtSignal
from .adapter import AgerhProvider
from . import service


class AgerhWorker(QThread):
    progress_changed = pyqtSignal(int, str)
    finished_success = pyqtSignal(dict)
    finished_error = pyqtSignal(str)

    def __init__(self, params: dict):
        super().__init__()
        self.params = params
        self.provider = AgerhProvider()

    def run(self):
        try:
            self.progress_changed.emit(10, "Conectando ao provedor AGERH...")
            
            # Executa a coleta via Adapter
            layers = self.provider.fetch(params=self.params)
            
            # Exportação GPKG se solicitado
            if self.params.get("output_mode") == "gpkg":
                gpkg_file = self.params.get("gpkg_path")
                if gpkg_file:
                    self.progress_changed.emit(90, f"Gravando GeoPackage: {gpkg_file}...")
                    service.save_layers_to_geopackage(layers, gpkg_file)

            self.progress_changed.emit(100, "Concluído com sucesso!")
            self.finished_success.emit(layers)
        except Exception as e:
            import traceback
            self.finished_error.emit(f"{str(e)}\n\n{traceback.format_exc()}")
