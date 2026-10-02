# -*- coding: utf-8 -*-
"""
Provedor Cemaden (Planejado).
Fonte: Centro Nacional de Monitoramento e Alertas de Desastres Naturais.
"""

from typing import List, Dict, Any, Optional
from ..base import BaseDataProvider, ProviderStatus


class CemadenProvider(BaseDataProvider):
    id = "cemaden"
    name = "Cemaden - PCDs Hidro"
    organization = "Centro Nacional de Monitoramento e Alertas de Desastres Naturais (MCTI)"
    theme = "agua"
    scope = "Nacional"
    status = ProviderStatus.PLANNED
    description = (
        "Rede de Plataformas de Coleta de Dados (PCDs) pluviométricas, hidrológicas e agrometeorológicas. "
        "Monitoramento contínuo em áreas de suscetibilidade a inundações bruscas e deslizamentos nos 78 municípios do ES."
    )
    website = "https://www.gov.br/cemaden"
    products = ["precipitacao", "niveis", "inundacoes", "extremos_hidrologicos"]

    def health_check(self) -> bool:
        return False

    def capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "cemaden_pcd_chuva",
                "name": "Pluviômetros Automáticos (Acumulados 1h, 24h, 72h)",
                "product": "precipitacao",
                "status": "Planejado",
                "protocol": "API REST Cemaden",
                "description": "Estações meteorológicas municipais com telemetria a cada 10 minutos."
            },
            {
                "id": "cemaden_pcd_rio",
                "name": "Sensores de Nível em Rios Urbanos",
                "product": "niveis",
                "status": "Planejado",
                "protocol": "API REST Cemaden",
                "description": "Sensores ultrassônicos e de pressão monitorando córregos e rios críticos."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        raise NotImplementedError(
            f"O conector '{self.name}' está previsto na arquitetura do QUALI+, "
            "mas ainda não possui conector operacional implementado no MVP."
        )
