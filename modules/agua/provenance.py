# -*- coding: utf-8 -*-
"""
Módulo de Rastreabilidade e Proveniência de Dados do QUALI+.
Registra e anexa metadados de auditoria e linhagem científica a cada camada gerada.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class DataProvenance:
    """
    Estrutura padronizada de metadados de proveniência do QUALI+.
    """

    def __init__(
        self,
        dimension: str = "agua",
        provider: str = "",
        organization: str = "",
        dataset: str = "",
        product: str = "",
        version: str = "1.0",
        observation_time: Optional[str] = None,
        processing_time: Optional[str] = None,
        territory: str = "Espírito Santo",
        algorithm: str = "Ingestão e Validação Direta",
        extra_metadata: Optional[Dict[str, Any]] = None
    ):
        self.dimension = dimension
        self.provider = provider
        self.organization = organization
        self.dataset = dataset
        self.product = product
        self.version = version
        self.retrieved_at = datetime.now(timezone.utc).isoformat()
        self.observation_time = observation_time or "Tempo Quase Real / Histórico Recente"
        self.processing_time = processing_time or datetime.now(timezone.utc).isoformat()
        self.territory = territory
        self.algorithm = algorithm
        self.extra_metadata = extra_metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "provider": self.provider,
            "organization": self.organization,
            "dataset": self.dataset,
            "product": self.product,
            "version": self.version,
            "retrieved_at": self.retrieved_at,
            "observation_time": self.observation_time,
            "processing_time": self.processing_time,
            "territory": self.territory,
            "algorithm": self.algorithm,
            "extra_metadata": self.extra_metadata
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def tag_layer(self, layer) -> None:
        """
        Anexa os metadados de proveniência diretamente nas propriedades da camada QGIS.
        """
        if not layer or not hasattr(layer, "setCustomProperty"):
            return

        layer.setCustomProperty("quali:dimension", self.dimension)
        layer.setCustomProperty("quali:provider", self.provider)
        layer.setCustomProperty("quali:organization", self.organization)
        layer.setCustomProperty("quali:dataset", self.dataset)
        layer.setCustomProperty("quali:product", self.product)
        layer.setCustomProperty("quali:version", self.version)
        layer.setCustomProperty("quali:retrieved_at", self.retrieved_at)
        layer.setCustomProperty("quali:observation_time", self.observation_time)
        layer.setCustomProperty("quali:territory", self.territory)
        layer.setCustomProperty("quali:algorithm", self.algorithm)
        layer.setCustomProperty("quali:provenance_json", self.to_json())

        # Anexa na descrição/abstract da camada para visualização no painel de metadados do QGIS
        desc = (
            f"QUALI+ • Dimensão: {self.dimension.upper()}\n"
            f"Fonte/Provedor: {self.provider.upper()} ({self.organization})\n"
            f"Produto Analítico: {self.product}\n"
            f"Conjunto de Dados: {self.dataset}\n"
            f"Território: {self.territory}\n"
            f"Coletado em: {self.retrieved_at}\n"
            f"Período de Observação: {self.observation_time}\n"
            f"Algoritmo: {self.algorithm}\n"
            f"Versão: {self.version}"
        )
        if hasattr(layer, "setAbstract"):
            layer.setAbstract(desc)
