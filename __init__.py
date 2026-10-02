# -*- coding: utf-8 -*-
"""
Ponto de entrada do plugin AGERH Hidro Dados para o QGIS.
"""


def classFactory(iface):
    """
    Carrega a classe AgerhPlugin a partir do arquivo agerh_plugin.py.
    """
    from .agerh_plugin import AgerhPlugin
    return AgerhPlugin(iface)
