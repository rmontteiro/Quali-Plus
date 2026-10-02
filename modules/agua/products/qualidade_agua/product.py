# -*- coding: utf-8 -*-
from ..base import BaseProduct

class QualidadeAguaProduct(BaseProduct):
    def __init__(self):
        super().__init__(
            id="qualidade_agua",
            name="Qualidade da Água (IQA)",
            category="Monitoramento",
            description="Índice de Qualidade da Água e parâmetros físico-químicos e biológicos (OD, DBO, turbidez, coliformes).",
            supported_providers=["agerh"]
        )
