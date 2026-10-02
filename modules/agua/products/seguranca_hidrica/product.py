# -*- coding: utf-8 -*-
from ..base import BaseProduct

class SegurancaHidricaProduct(BaseProduct):
    def __init__(self):
        super().__init__(
            id="seguranca_hidrica",
            name="Segurança Hídrica e Balanço",
            category="Planejamento",
            description="Balanço hídrico por bacia, demandas outorgadas vs vazão de referência (Q90) e vulnerabilidade hídrica.",
            supported_providers=["agerh", "ana_snirh", "monitor_secas", "mapbiomas_agua"]
        )
