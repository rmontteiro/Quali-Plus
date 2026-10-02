# -*- coding: utf-8 -*-
"""
Provedor NASA / GPM IMERG (Planejado).
Fonte: NASA / JAXA.
"""

from typing import List, Dict, Any, Optional
from ..base import BaseDataProvider, ProviderStatus


class NasaGpmProvider(BaseDataProvider):
    id = "gpm_imerg"
    name = "NASA / JAXA - GPM IMERG"
    organization = "NASA / JAXA"
    theme = "agua"
    scope = "Global"
    status = ProviderStatus.PLANNED
    description = (
        "Integrated Multi-satellitE Retrievals for GPM (IMERG). "
        "Produto de sensoriamento remoto multissatélite calibrado que combina dados de micro-ondas passivas e infravermelho "
        "para estimar taxas e acumulados de precipitação a cada 30 minutos em resolução de 0.1° (~10 km)."
    )
    website = "https://gpm.nasa.gov"
    products = ["precipitacao", "extremos_hidrologicos"]

    def health_check(self) -> bool:
        return False

    def capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "imerg_early",
                "name": "GPM IMERG Early (Quase Tempo Real - 4h de latência)",
                "product": "precipitacao",
                "status": "Planejado",
                "protocol": "NASA GES DISC OpenDAP / Cloud COG",
                "description": "Acumulados de chuva para monitoramento de eventos extremos e cheias."
            },
            {
                "id": "imerg_final",
                "name": "GPM IMERG Final (Pesquisa e Climatologia)",
                "product": "precipitacao",
                "status": "Planejado",
                "protocol": "NASA Earthdata Cloud",
                "description": "Série histórica calibrada com pluviômetros de superfície desde o ano 2000."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        raise NotImplementedError(
            f"O conector '{self.name}' está previsto na arquitetura do QUALI+, "
            "mas ainda não possui conector operacional implementado no MVP."
        )
