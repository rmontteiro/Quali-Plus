# -*- coding: utf-8 -*-
"""
Provedor GloFAS (Planejado).
Fonte: Copernicus Emergency Management Service / ECMWF.
"""

from typing import List, Dict, Any, Optional
from ..base import BaseDataProvider, ProviderStatus


class GlofasProvider(BaseDataProvider):
    id = "glofas"
    name = "GloFAS - Global Flood Awareness"
    organization = "Copernicus Emergency Management Service / ECMWF"
    theme = "agua"
    scope = "Global"
    status = ProviderStatus.PLANNED
    description = (
        "Global Flood Awareness System (GloFAS). Sistema global de previsão de vazões e probabilidade de "
        "inundações fluviais em horizontes de 1 a 30 dias, acoplado ao modelo hidrológico LISFLOOD e dados ECMWF."
    )
    website = "https://www.globalfloods.eu"
    products = ["vazoes", "inundacoes", "extremos_hidrologicos"]

    def health_check(self) -> bool:
        return False

    def capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "glofas_forecast_discharge",
                "name": "Previsão Ensemble de Vazão Fluvial (1 a 30 dias)",
                "product": "vazoes",
                "status": "Planejado",
                "protocol": "Copernicus Climate Data Store (CDS) API",
                "description": "Previsões diárias de vazão com períodos de retorno de 2, 5 e 20 anos."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        raise NotImplementedError(
            f"O conector '{self.name}' está previsto na arquitetura do QUALI+, "
            "mas ainda não possui conector operacional implementado no MVP."
        )
