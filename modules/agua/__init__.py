# -*- coding: utf-8 -*-
"""
Módulo ÁGUA do QUALI+.
Dimensão temática agregadora de múltiplas fontes estaduais, nacionais e globais.
"""

from .base import BaseDataProvider, ProviderStatus, BaseProduct
from .provenance import DataProvenance
from .registry import SourceRegistry, ProductRegistry
from .providers.agerh.adapter import AgerhProvider
from .ui.dialog import QualiAguaDialog

__all__ = [
    "BaseDataProvider",
    "ProviderStatus",
    "BaseProduct",
    "DataProvenance",
    "SourceRegistry",
    "ProductRegistry",
    "AgerhProvider",
    "QualiAguaDialog"
]
