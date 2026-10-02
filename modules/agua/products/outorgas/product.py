# -*- coding: utf-8 -*-
from ..base import BaseProduct

class OutorgasProduct(BaseProduct):
    def __init__(self):
        super().__init__(
            id="outorgas",
            name="Outorgas e Usos da Água",
            category="Gestão Hídrica",
            description="Cadastros de outorga, captações superficiais, poços subterrâneos, barramentos e lançamentos.",
            supported_providers=["agerh", "ana_snirh"]
        )
