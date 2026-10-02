# -*- coding: utf-8 -*-
"""
Provedor ANA / SNIRH (Planejado).
Fonte: Agência Nacional de Águas e Saneamento Básico.
"""

from typing import List, Dict, Any, Optional
from ..base import BaseDataProvider, ProviderStatus


class AnaProvider(BaseDataProvider):
    id = "ana_snirh"
    name = "ANA / SNIRH / Hidroweb"
    organization = "Agência Nacional de Águas e Saneamento Básico (ANA)"
    theme = "agua"
    scope = "Nacional"
    status = ProviderStatus.PLANNED
    description = (
        "Sistema Nacional de Informações sobre Recursos Hídricos (SNIRH). "
        "Rede Hidrometeorológica Nacional (RHN), estações telemétricas e convencionais de nível, "
        "vazão e chuva, além da base de outorgas de corpos hídricos de domínio da União."
    )
    website = "https://www.snirh.gov.br"
    products = ["niveis", "vazoes", "precipitacao", "outorgas", "reservatorios"]

    def health_check(self) -> bool:
        return False

    def capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "telemetria_rhn",
                "name": "Estações Telemétricas RHN",
                "product": "niveis",
                "status": "Planejado",
                "protocol": "API REST HidroWeb v2",
                "description": "Séries horárias de cotas e vazões em tempo quase-real."
            },
            {
                "id": "outorgas_uniao",
                "name": "Outorgas de Domínio da União",
                "product": "outorgas",
                "status": "Planejado",
                "protocol": "WFS / GeoJSON SNIRH",
                "description": "Captações e barramentos em rios federais (ex: Rio Doce)."
            },
            {
                "id": "sar_reservatorios",
                "name": "Acompanhamento de Reservatórios (SAR)",
                "product": "reservatorios",
                "status": "Planejado",
                "protocol": "API REST SAR",
                "description": "Volumes acumulados e cotas de reservatórios de hidrelétricas e regularização."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        raise NotImplementedError(
            f"O conector '{self.name}' está previsto na arquitetura do QUALI+, "
            "mas ainda não possui conector operacional implementado no MVP."
        )
