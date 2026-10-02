# -*- coding: utf-8 -*-
"""
Provedor Copernicus Sentinel-1 SAR (Planejado).
Fonte: European Space Agency (ESA) / Copernicus.
"""

from typing import List, Dict, Any, Optional
from ..base import BaseDataProvider, ProviderStatus


class Sentinel1Provider(BaseDataProvider):
    id = "sentinel1"
    name = "Copernicus Sentinel-1 SAR"
    organization = "European Space Agency (ESA) / Copernicus"
    theme = "agua"
    scope = "Global"
    status = ProviderStatus.PLANNED
    description = (
        "Satélites de radar de abertura sintética (SAR em banda C). "
        "Permite a detecção de lâmina de água e mapeamento emergencial de manchas de inundação "
        "dia e noite, mesmo sob densa cobertura de nuvens e chuva torrencial."
    )
    website = "https://dataspace.copernicus.eu"
    products = ["inundacoes", "reservatorios"]

    def health_check(self) -> bool:
        return False

    def capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "mancha_inundacao_sar",
                "name": "Manchas de Inundação Detectadas por Radar SAR",
                "product": "inundacoes",
                "status": "Planejado",
                "protocol": "Copernicus Data Space Ecosystem STAC API",
                "description": "Polígonos vetoriais e máscaras raster de cheia derivados de Sentinel-1 GRD."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        raise NotImplementedError(
            f"O conector '{self.name}' está previsto na arquitetura do QUALI+, "
            "mas ainda não possui conector operacional implementado no MVP."
        )
