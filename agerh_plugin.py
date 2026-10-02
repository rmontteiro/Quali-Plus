# -*- coding: utf-8 -*-
"""
Classe principal de integração do Plugin QUALI+ (Módulo Água) com o QGIS.
"""

import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu

from .modules.agua.ui.dialog import QualiAguaDialog


class AgerhPlugin:
    """
    Plugin QUALI+ para o QGIS - Dimensão Temática ÁGUA.
    Conecta múltiplas fontes de dados hidrológicos, operando inicialmente com o conector AGERH.
    """

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action_agua = None
        self.menu_quali = None
        self.dialog = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        # Ação principal da Dimensão Água
        self.action_agua = QAction(icon, "QUALI+ • Dimensão Água", self.iface.mainWindow())
        self.action_agua.setStatusTip("QUALI+ • Plataforma de Recursos Hídricos (AGERH, ANA, SGB, Cemaden, GloFAS...)")
        self.action_agua.triggered.connect(self.run)

        # Adiciona na barra de ferramentas do QGIS
        self.iface.addToolBarIcon(self.action_agua)

        # Adiciona no menu Web do QGIS
        self.iface.addPluginToWebMenu("QUALI+ • Recursos Hídricos", self.action_agua)

        # Cria menu principal 'QUALI+' na barra de menus do QGIS
        menu_bar = self.iface.mainWindow().menuBar()
        self.menu_quali = QMenu("QUALI+", menu_bar)
        self.menu_quali.addAction(self.action_agua)
        menu_bar.addMenu(self.menu_quali)

    def unload(self):
        if self.action_agua:
            self.iface.removePluginWebMenu("QUALI+ • Recursos Hídricos", self.action_agua)
            self.iface.removeToolBarIcon(self.action_agua)

        if self.menu_quali:
            menu_bar = self.iface.mainWindow().menuBar()
            menu_bar.removeAction(self.menu_quali.menuAction())

        if self.dialog:
            self.dialog.close()

    def run(self):
        if not self.dialog:
            self.dialog = QualiAguaDialog(self.iface, parent=self.iface.mainWindow())
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
