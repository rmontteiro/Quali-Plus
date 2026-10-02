# -*- coding: utf-8 -*-
"""
Provedor MapBiomas Água (Planejado).
Fonte: Rede MapBiomas.
"""

from typing import List, Dict, Any, Optional
from ..base import BaseDataProvider, ProviderStatus


class MapbiomasAguaProvider(BaseDataProvider):
    id = "mapbiomas_agua"
    name = "MapBiomas Água"
    organization = "Rede MapBiomas"
    theme = "agua"
    scope = "Nacional"
    status = ProviderStatus.PLANNED
    description = (
        "Mapeamento da dinâmica da superfície de água no Brasil de 1985 a 2024. "
        "Séries históricas anuais e mensais de corpos hídricos naturais e reservatórios antrópicos no ES."
    )
    website = "https://plataforma.agua.mapbiomas.org"
    products = ["reservatorios", "seguranca_hidrica"]

    def health_check(self) -> bool:
        return False

    def capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "superficie_agua_anual",
                "name": "Superfície de Água Anual (1985-2024)",
                "product": "reservatorios",
                "status": "Planejado",
                "protocol": "Google Earth Engine Asset / GeoTIFF",
                "description": "Lâmina de água anual classificada a partir de imagens Landsat (30m)."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        raise NotImplementedError(
            f"O conector '{self.name}' está previsto na arquitetura do QUALI+, "
            "mas ainda não possui conector operacional implementado no MVP."
        )
