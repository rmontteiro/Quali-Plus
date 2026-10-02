# -*- coding: utf-8 -*-
from ..base import BaseProduct

class HidrologiaProduct(BaseProduct):
    def __init__(self):
        super().__init__(
            id="hidrologia",
            name="Hidrologia (Níveis e Vazões)",
            category="Hidrometria",
            description="Medições telemétricas de cotas fluviométricas e vazões em rios capixabas e bacias federais.",
            supported_providers=["ana_snirh", "sgb_sace", "cemaden", "glofas"]
        )
