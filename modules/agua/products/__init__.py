# -*- coding: utf-8 -*-
from .base import BaseProduct
from .qualidade_agua import QualidadeAguaProduct
from .hidrologia import HidrologiaProduct
from .precipitacao import PrecipitacaoProduct
from .inundacao import InundacaoProduct
from .outorgas import OutorgasProduct
from .seguranca_hidrica import SegurancaHidricaProduct

__all__ = [
    "BaseProduct",
    "QualidadeAguaProduct",
    "HidrologiaProduct",
    "PrecipitacaoProduct",
    "InundacaoProduct",
    "OutorgasProduct",
    "SegurancaHidricaProduct"
]
