# -*- coding: utf-8 -*-
"""
Contratos base para provedores de dados e produtos analíticos
da dimensão temática Água do QUALI+.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ProviderStatus:
    AVAILABLE = "available"            # Operacional / Integrado
    PLANNED = "planned"                # Previsto no White Paper / Roadmap
    NOT_INTEGRATED = "not_integrated"  # Mapeado conceitualmente, não integrado


class BaseDataProvider(ABC):
    """
    Abstração comum para todas as fontes de dados da dimensão Água.
    Cada fonte (estadual, nacional ou global) deve implementar esta classe.
    """

    id: str = ""
    name: str = ""
    organization: str = ""
    theme: str = "agua"
    scope: str = "Estadual"            # "Estadual", "Nacional", "Global"
    status: str = ProviderStatus.PLANNED
    description: str = ""
    website: str = ""
    products: List[str] = []

    def __init__(self):
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verifica a conectividade e disponibilidade da fonte."""
        pass

    @abstractmethod
    def capabilities(self) -> List[Dict[str, Any]]:
        """Retorna a lista de produtos, camadas e formatos suportados pela fonte."""
        pass

    @abstractmethod
    def fetch(self, product_id: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Executa a coleta e processamento de um produto específico da fonte."""
        pass


class BaseProduct:
    """
    Representação conceitual de um produto analítico da dimensão Água.
    Ex: Qualidade da água, Vazões, Precipitação, Outorgas, Inundações.
    """

    id: str = ""
    name: str = ""
    category: str = ""
    description: str = ""
    supported_providers: List[str] = []

    def __init__(self, id: str, name: str, category: str, description: str, supported_providers: Optional[List[str]] = None):
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self.supported_providers = supported_providers or []
