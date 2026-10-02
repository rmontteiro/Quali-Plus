# -*- coding: utf-8 -*-
"""
Provedor SGB / CPRM - SACE (Planejado).
Fonte: Serviço Geológico do Brasil.
"""

from typing import List, Dict, Any, Optional
from ..base import BaseDataProvider, ProviderStatus


class SgbProvider(BaseDataProvider):
    id = "sgb_sace"
    name = "SGB / CPRM - SACE"
    organization = "Serviço Geológico do Brasil (SGB / CPRM)"
    theme = "agua"
    scope = "Nacional"
    status = ProviderStatus.PLANNED
    description = (
        "Sistemas de Alerta Hidrológico (SACE) operados pelo SGB para as bacias hidrográficas "
        "do Rio Doce e do Rio Itabapoana. Cotas linimétricas de atenção, alerta e inundação, "
        "com modelos hidrológicos de previsão de pico de cheia."
    )
    website = "https://www.sgb.gov.br/sace"
    products = ["niveis", "vazoes", "inundacoes", "extremos_hidrologicos"]

    def health_check(self) -> bool:
        return False

    def capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "sace_alertas",
                "name": "Cotas de Alerta e Inundação (SACE)",
                "product": "inundacoes",
                "status": "Planejado",
                "protocol": "API REST SACE SGB",
                "description": "Limiares hidrológicos de atenção, alerta e inundação para bacias do ES."
            },
            {
                "id": "sace_previsao",
                "name": "Previsões de Vazão e Cota",
                "product": "vazoes",
                "status": "Planejado",
                "protocol": "API REST SACE SGB",
                "description": "Previsões hidrológicas de nível em horizontes de 12h a 48h."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        raise NotImplementedError(
            f"O conector '{self.name}' está previsto na arquitetura do QUALI+, "
            "mas ainda não possui conector operacional implementado no MVP."
        )
