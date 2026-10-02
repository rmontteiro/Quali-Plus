# -*- coding: utf-8 -*-
"""
Registro Central de Fontes de Dados (SourceRegistry) e Produtos Analíticos (ProductRegistry)
da dimensão temática Água do QUALI+.
"""

from typing import Dict, List, Any, Optional
from .base import ProviderStatus, BaseProduct, BaseDataProvider


class SourceRegistry:
    """
    Catálogo central de fontes / provedores da dimensão Água.
    Permite registrar novas fontes dinamicamente sem alterar a navegação estrutural do QUALI+.
    """

    _providers: Dict[str, Dict[str, Any]] = {}
    _instances: Dict[str, BaseDataProvider] = {}

    @classmethod
    def register(
        cls,
        id: str,
        name: str,
        organization: str,
        dimension: str = "agua",
        status: str = ProviderStatus.PLANNED,
        scope: str = "Estadual",
        description: str = "",
        website: str = "",
        products: Optional[List[str]] = None,
        provider_class: Optional[type] = None
    ) -> None:
        """Registra uma nova fonte no catálogo central."""
        cls._providers[id] = {
            "id": id,
            "name": name,
            "organization": organization,
            "dimension": dimension,
            "status": status,
            "scope": scope,
            "description": description,
            "website": website,
            "products": products or [],
            "provider_class": provider_class
        }

    @classmethod
    def get(cls, id: str) -> Optional[Dict[str, Any]]:
        return cls._providers.get(id)

    @classmethod
    def get_instance(cls, id: str) -> Optional[BaseDataProvider]:
        if id not in cls._instances:
            info = cls.get(id)
            if info and info.get("provider_class"):
                cls._instances[id] = info["provider_class"]()
        return cls._instances.get(id)

    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        return list(cls._providers.values())

    @classmethod
    def list_by_status(cls, status: str) -> List[Dict[str, Any]]:
        return [p for p in cls._providers.values() if p["status"] == status]

    @classmethod
    def list_by_product(cls, product_id: str) -> List[Dict[str, Any]]:
        return [p for p in cls._providers.values() if product_id in p.get("products", [])]


class ProductRegistry:
    """
    Catálogo de produtos analíticos da dimensão Água.
    """

    _products: Dict[str, BaseProduct] = {}

    @classmethod
    def register(cls, product: BaseProduct) -> None:
        cls._products[product.id] = product

    @classmethod
    def get(cls, product_id: str) -> Optional[BaseProduct]:
        return cls._products.get(product_id)

    @classmethod
    def list_all(cls) -> List[BaseProduct]:
        return list(cls._products.values())


# ==============================================================================
# INICIALIZAÇÃO DO REGISTRO DE FONTES (WHITE PAPER QUALI+ - DIMENSÃO ÁGUA)
# ==============================================================================

# 1. AGERH (Operacional / Disponível)
SourceRegistry.register(
    id="agerh",
    name="AGERH / HidroAgerh",
    organization="AGERH - Espírito Santo",
    dimension="agua",
    status=ProviderStatus.AVAILABLE,
    scope="Estadual",
    description="Agência Estadual de Recursos Hídricos do Espírito Santo. Monitoramento da qualidade da água (IQA) e cadastro estadual de outorgas e interferências hídricas.",
    website="https://hidro.agerh.es.gov.br",
    products=["qualidade_agua", "outorgas", "interferencias", "seguranca_hidrica"]
)

# 2. ANA / SNIRH (Planejado)
SourceRegistry.register(
    id="ana_snirh",
    name="ANA / SNIRH / Hidroweb",
    organization="Agência Nacional de Águas e Saneamento Básico (ANA)",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Nacional",
    description="Sistema Nacional de Informações sobre Recursos Hídricos. Rede Hidrometeorológica Nacional (RHN), telemetria em tempo real, cotas, vazões e outorgas de corpos hídricos federais.",
    website="https://www.snirh.gov.br",
    products=["niveis", "vazoes", "precipitacao", "outorgas", "reservatorios"]
)

# 3. SGB / SACE (Planejado)
SourceRegistry.register(
    id="sgb_sace",
    name="SGB / CPRM - SACE",
    organization="Serviço Geológico do Brasil (SGB / CPRM)",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Nacional",
    description="Sistema de Alerta Hidrológico da Bacia do Rio Doce e Bacia do Rio Itabapoana. Cotas de alerta, inundação e previsões hidrológicas de cheias.",
    website="https://www.sgb.gov.br/sace",
    products=["niveis", "vazoes", "inundacoes", "extremos_hidrologicos"]
)

# 4. Cemaden (Planejado)
SourceRegistry.register(
    id="cemaden",
    name="Cemaden - PCDs Hidro",
    organization="Centro Nacional de Monitoramento e Alertas de Desastres Naturais",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Nacional",
    description="Rede de Plataformas de Coleta de Dados (PCDs) pluviométricas e hidrológicas voltadas à prevenção e alerta antecipado de desastres hidrológicos nos municípios capixabas.",
    website="https://www.gov.br/cemaden",
    products=["precipitacao", "niveis", "inundacoes", "extremos_hidrologicos"]
)

# 5. Monitor de Secas (Planejado)
SourceRegistry.register(
    id="monitor_secas",
    name="Monitor de Secas",
    organization="ANA / AGERH / SEAMA",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Nacional/Estadual",
    description="Acompanhamento contínuo da severidade de estiagem e secas no Espírito Santo (seca fraca a excepcional) e seus impactos nos recursos hídricos e agricultura.",
    website="https://monitordesecas.ana.gov.br",
    products=["extremos_hidrologicos", "seguranca_hidrica"]
)

# 6. AlertaES (Planejado)
SourceRegistry.register(
    id="alerta_es",
    name="AlertaES / Defesa Civil Estadual",
    organization="Governo do Estado do Espírito Santo (CBMES / CEPDEC)",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Estadual",
    description="Avisos, alertas e relatórios operacionais de risco hidrológico de inundação, enxurrada e alagamento emitidos pela Defesa Civil do ES.",
    website="https://defesacivil.es.gov.br",
    products=["inundacoes", "extremos_hidrologicos"]
)

# 7. GloFAS (Planejado)
SourceRegistry.register(
    id="glofas",
    name="GloFAS - Global Flood Awareness",
    organization="Copernicus Emergency Management Service / ECMWF",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Global",
    description="Sistema Global de Alerta de Inundações acoplado a modelos hidrológicos transfronteiriços com previsões de vazão e probabilidade de cheia de 1 a 30 dias.",
    website="https://www.globalfloods.eu",
    products=["vazoes", "inundacoes", "extremos_hidrologicos"]
)

# 8. NASA / GPM IMERG (Planejado)
SourceRegistry.register(
    id="gpm_imerg",
    name="NASA / JAXA - GPM IMERG",
    organization="NASA / JAXA",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Global",
    description="Global Precipitation Measurement (IMERG). Estimativa de chuva global calibrada por satélite em tempo quase-real com resolução espacial de 0.1° (~10 km).",
    website="https://gpm.nasa.gov",
    products=["precipitacao", "extremos_hidrologicos"]
)

# 9. MapBiomas Água (Planejado)
SourceRegistry.register(
    id="mapbiomas_agua",
    name="MapBiomas Água",
    organization="Rede MapBiomas",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Nacional",
    description="Mapeamento histórico e dinâmico da superfície de lâmina de água, rios, lagos e reservatórios no Espírito Santo de 1985 até o presente.",
    website="https://plataforma.agua.mapbiomas.org",
    products=["reservatorios", "seguranca_hidrica"]
)

# 10. Sentinel-1 SAR (Planejado)
SourceRegistry.register(
    id="sentinel1",
    name="Copernicus Sentinel-1 SAR",
    organization="European Space Agency (ESA)",
    dimension="agua",
    status=ProviderStatus.PLANNED,
    scope="Global",
    description="Imagens de radar de abertura sintética (SAR) para detecção de corpos hídricos e mapeamento de manchas de inundação em tempo de evento de desastre, mesmo com nuvens.",
    website="https://dataspace.copernicus.eu",
    products=["inundacoes", "reservatorios"]
)


# ==============================================================================
# INICIALIZAÇÃO DO REGISTRO DE PRODUTOS ANALÍTICOS (DIMENSÃO ÁGUA)
# ==============================================================================

ProductRegistry.register(BaseProduct(
    id="qualidade_agua",
    name="Qualidade da Água (IQA)",
    category="Monitoramento",
    description="Rede de monitoramento com estações de coleta e parâmetros físico-químicos (OD, DBO, turbidez, coliformes, pH) e índice IQA.",
    supported_providers=["agerh"]
))

ProductRegistry.register(BaseProduct(
    id="outorgas",
    name="Outorgas de Direito de Uso",
    category="Gestão Hídrica",
    description="Cadastros e autorizações de uso de recursos hídricos superficiais e subterrâneos.",
    supported_providers=["agerh", "ana_snirh"]
))

ProductRegistry.register(BaseProduct(
    id="interferencias",
    name="Interferências Hídricas",
    category="Gestão Hídrica",
    description="Vazões captadas e lançadas, balanço hídrico, vazão Q90, vazão média e vazões requeridas mensais.",
    supported_providers=["agerh"]
))

ProductRegistry.register(BaseProduct(
    id="niveis",
    name="Níveis Fluviométricos (Cotas)",
    category="Hidrometria",
    description="Medições de cota de réguas linimétricas e sensores telemétricos em tempo real.",
    supported_providers=["ana_snirh", "sgb_sace", "cemaden"]
))

ProductRegistry.register(BaseProduct(
    id="vazoes",
    name="Vazões Fluviais",
    category="Hidrometria",
    description="Séries históricas e estimativas em tempo real de vazão de rios (m³/s ou L/s).",
    supported_providers=["ana_snirh", "sgb_sace", "glofas"]
))

ProductRegistry.register(BaseProduct(
    id="precipitacao",
    name="Precipitação Pluviométrica",
    category="Hidrometeorologia",
    description="Acumulados de chuva horários, diários e mensais por pluviômetros de superfície e estimativas por satélite.",
    supported_providers=["cemaden", "ana_snirh", "gpm_imerg"]
))

ProductRegistry.register(BaseProduct(
    id="inundacao",
    name="Inundações e Manchas de Cheia",
    category="Risco e Desastres",
    description="Modelagem de cheias, manchas de inundação por radar SAR e alertas de cota de transbordamento.",
    supported_providers=["sgb_sace", "cemaden", "alerta_es", "glofas", "sentinel1"]
))

ProductRegistry.register(BaseProduct(
    id="extremos_hidrologicos",
    name="Extremos Hidrológicos",
    category="Resiliência Climática",
    description="Análise integrada de secas, estiagens severas e tempestades com risco de cheia.",
    supported_providers=["monitor_secas", "glofas", "cemaden", "alerta_es"]
))

ProductRegistry.register(BaseProduct(
    id="reservatorios",
    name="Reservatórios e Barramentos",
    category="Armazenamento",
    description="Volumes acumulados, cotas e monitoramento de superfície de água em reservatórios e barramentos.",
    supported_providers=["ana_snirh", "mapbiomas_agua", "sentinel1"]
))

ProductRegistry.register(BaseProduct(
    id="seguranca_hidrica",
    name="Segurança Hídrica e Balanço",
    category="Planejamento",
    description="Indicadores de disponibilidade hídrica, estresse hídrico por bacia e segurança de abastecimento.",
    supported_providers=["agerh", "ana_snirh", "monitor_secas", "mapbiomas_agua"]
))
