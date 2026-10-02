# -*- coding: utf-8 -*-
"""
Provedor Monitor de Secas (Planejado).
Fonte: ANA / AGERH / SEAMA.
"""

from typing import List, Dict, Any, Optional
from ..base import BaseDataProvider, ProviderStatus


class MonitorSecasProvider(BaseDataProvider):
    id = "monitor_secas"
    name = "Monitor de Secas"
    organization = "ANA / AGERH / SEAMA"
    theme = "agua"
    scope = "Nacional/Estadual"
    status = ProviderStatus.PLANNED
    description = (
        "Processo de acompanhamento regular e periódico da situação da seca no Espírito Santo, "
        "com mapas mensais de severidade (seca fraca S0 a excepcional S4), impactos nos recursos hídricos "
        "e indicadores de curto e longo prazo."
    )
    website = "https://monitordesecas.ana.gov.br"
    products = ["extremos_hidrologicos", "seguranca_hidrica"]

    def health_check(self) -> bool:
        return False

    def capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "mapas_severidade_seca",
                "name": "Polígonos Mensais de Severidade de Seca (S0 a S4)",
                "product": "extremos_hidrologicos",
                "status": "Planejado",
                "protocol": "WFS / Shapefile ANA",
                "description": "Recorte vetorial mensal da seca no território do Espírito Santo."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        raise NotImplementedError(
            f"O conector '{self.name}' está previsto na arquitetura do QUALI+, "
            "mas ainda não possui conector operacional implementado no MVP."
        )
