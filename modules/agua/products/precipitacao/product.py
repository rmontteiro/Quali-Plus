# -*- coding: utf-8 -*-
from ..base import BaseProduct

class PrecipitacaoProduct(BaseProduct):
    def __init__(self):
        super().__init__(
            id="precipitacao",
            name="Precipitação Pluviométrica",
            category="Hidrometeorologia",
            description="Chuva acumulada em 1h, 24h, 72h e mensal por pluviômetros automáticos e estimativas de satélite.",
            supported_providers=["cemaden", "ana_snirh", "gpm_imerg"]
        )
