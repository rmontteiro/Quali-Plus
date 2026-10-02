# -*- coding: utf-8 -*-
from ..base import BaseProduct

class InundacaoProduct(BaseProduct):
    def __init__(self):
        super().__init__(
            id="inundacao",
            name="Inundações e Manchas de Cheia",
            category="Risco e Desastres",
            description="Limiares de inundação, alertas de transbordamento de calha e manchas de água por radar SAR.",
            supported_providers=["sgb_sace", "cemaden", "alerta_es", "glofas", "sentinel1"]
        )
