# -*- coding: utf-8 -*-
"""
Adapter operacional do conector AGERH para a arquitetura de provedores QUALI+.
Implementa o contrato BaseDataProvider e adiciona rastreabilidade (DataProvenance).
"""

from typing import List, Dict, Any, Optional
import urllib.request
import ssl

from ...base import BaseDataProvider, ProviderStatus
from ...provenance import DataProvenance
from . import service


class AgerhProvider(BaseDataProvider):
    """
    Conector operacional para os dados da AGERH-ES dentro da dimensão Água do QUALI+.
    """

    id = "agerh"
    name = "AGERH / HidroAgerh"
    organization = "AGERH - Espírito Santo"
    theme = "agua"
    scope = "Estadual"
    status = ProviderStatus.AVAILABLE
    description = (
        "Agência Estadual de Recursos Hídricos do Espírito Santo. "
        "Monitoramento da qualidade da água (IQA) e base cadastral de outorgas e interferências hídricas."
    )
    website = "https://hidro.agerh.es.gov.br"
    products = ["qualidade_agua", "outorgas", "interferencias", "seguranca_hidrica"]

    def __init__(self):
        super().__init__()

    def health_check(self) -> bool:
        """Verifica se os servidores da AGERH estão acessíveis."""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(
                service.URLS["bacias"],
                headers={"User-Agent": "QUALI-Plus/1.0 (HealthCheck)"}
            )
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                return resp.status == 200
        except Exception:
            return False

    def capabilities(self) -> List[Dict[str, Any]]:
        """Retorna as capacidades e camadas suportadas pelo conector AGERH."""
        return [
            {
                "id": "pontos_coleta",
                "name": "Pontos de Coleta IQA",
                "product": "qualidade_agua",
                "geometry": "Point",
                "crs": "EPSG:4326",
                "description": "Estações de monitoramento da qualidade da água no Espírito Santo."
            },
            {
                "id": "dados_iqa",
                "name": "Histórico de Medições IQA",
                "product": "qualidade_agua",
                "geometry": "None (Tabela)",
                "crs": None,
                "description": "Séries históricas físico-químicas (53 parâmetros de análise de água)."
            },
            {
                "id": "outorgas",
                "name": "Outorgas de Recursos Hídricos",
                "product": "outorgas",
                "geometry": "Point",
                "crs": "EPSG:31984",
                "description": "Cadastros de outorga de direito de uso de água superficial e subterrânea."
            },
            {
                "id": "interferencias",
                "name": "Interferências de Outorga",
                "product": "interferencias",
                "geometry": "None (Tabela)",
                "crs": None,
                "description": "Detalhamento de vazões outorgadas, Q90, vazão média e vazões requeridas mensais."
            },
            {
                "id": "bacias",
                "name": "Bacias Hidrográficas",
                "product": "seguranca_hidrica",
                "geometry": "None (Tabela)",
                "crs": None,
                "description": "Relação oficial de bacias hidrográficas estaduais."
            },
            {
                "id": "corpos_hidricos",
                "name": "Corpos Hídricos Cadastrados",
                "product": "seguranca_hidrica",
                "geometry": "None (Tabela)",
                "crs": None,
                "description": "Relação oficial de rios, córregos e lagoas monitoradas."
            }
        ]

    def fetch(self, product_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Executa a coleta através do AgerhDataLoader e anexa a proveniência aos resultados.
        """
        params = params or {}
        force_refresh = params.get("force_refresh", False)
        loader = service.AgerhDataLoader(force_refresh=force_refresh)

        results = {}

        # 1. Carregamento de dados auxiliares se necessário
        need_iqa = params.get("load_iqa_table", False) or (
            params.get("load_pontos", True) and params.get("enrich_iqa", True)
        )
        dados_iqa = None
        if need_iqa:
            filter_bacia = params.get("filter_bacia")
            dados_iqa = loader.load_dados_iqa(filter_bacia=filter_bacia if filter_bacia != "Todas as Bacias" else None)

        need_interf = params.get("load_interf_table", False) or (
            params.get("load_outorgas", True) and params.get("enrich_outorga", True)
        )
        interf_records = None
        if need_interf:
            interf_records = loader.load_interferencias()

        # 2. Pontos de Coleta
        if params.get("load_pontos", True):
            pts_data = loader.load_pontos_coleta(
                filter_situacao=params.get("filter_situacao"),
                filter_municipio=params.get("filter_municipio") if params.get("filter_municipio") != "Todos os Municípios (78)" else None,
                filter_bacia=params.get("filter_bacia") if params.get("filter_bacia") != "Todas as Bacias" else None
            )
            layer_pts = service.build_pontos_coleta_layer(
                pts_data,
                dados_iqa_records=dados_iqa,
                enrich=params.get("enrich_iqa", True)
            )
            if params.get("auto_style", True):
                service.apply_iqa_style(layer_pts)

            prov_pts = DataProvenance(
                dimension="agua",
                provider="agerh",
                organization="AGERH",
                dataset="pontos_coleta",
                product="qualidade_agua",
                version="1.0",
                territory="Espírito Santo",
                algorithm="Ingestão XML HidroAgerh + Junção da Última Medição IQA"
            )
            prov_pts.tag_layer(layer_pts)
            results["AGERH - Pontos de Coleta (IQA)"] = layer_pts

        # 3. Outorgas
        if params.get("load_outorgas", True):
            out_data = loader.load_outorgas(
                filter_municipio=params.get("filter_municipio") if params.get("filter_municipio") != "Todos os Municípios (78)" else None,
                filter_regiao=params.get("filter_bacia") if params.get("filter_bacia") != "Todas as Bacias" else None,
                filter_status=params.get("filter_status"),
                filter_tipo=params.get("filter_tipo")
            )
            layer_out = service.build_outorgas_layer(
                out_data,
                interferencias_records=interf_records,
                enrich=params.get("enrich_outorga", True)
            )
            if params.get("auto_style", True):
                service.apply_outorgas_style(layer_out)

            prov_out = DataProvenance(
                dimension="agua",
                provider="agerh",
                organization="AGERH",
                dataset="outorgas",
                product="outorgas",
                version="1.0",
                territory="Espírito Santo",
                algorithm="Ingestão XML HidroAgerh + Conversão SIRGAS 2000 UTM 24S + Junção de Vazões"
            )
            prov_out.tag_layer(layer_out)
            results["AGERH - Outorgas"] = layer_out

        # 4. Tabela Histórico IQA
        if params.get("load_iqa_table", False) and dados_iqa:
            tbl_iqa = service.build_dados_iqa_table(dados_iqa)
            prov_iqa = DataProvenance(
                dimension="agua",
                provider="agerh",
                organization="AGERH",
                dataset="dados_iqa",
                product="qualidade_agua",
                version="1.0",
                territory="Espírito Santo",
                algorithm="Ingestão de Parâmetros Físico-Químicos HidroAgerh"
            )
            prov_iqa.tag_layer(tbl_iqa)
            results["AGERH - Histórico IQA"] = tbl_iqa

        # 5. Tabela Interferências
        if params.get("load_interf_table", False) and interf_records:
            tbl_interf = service.build_interferencias_table(interf_records)
            prov_interf = DataProvenance(
                dimension="agua",
                provider="agerh",
                organization="AGERH",
                dataset="interferencias",
                product="interferencias",
                version="1.0",
                territory="Espírito Santo",
                algorithm="Ingestão de Balanço Hídrico e Vazões Mensais HidroAgerh"
            )
            prov_interf.tag_layer(tbl_interf)
            results["AGERH - Interferências"] = tbl_interf

        # 6. Bacias e Corpos Hídricos
        if params.get("load_bacias", False):
            tbl_b = service.build_bacias_table(loader.load_bacias())
            DataProvenance(dimension="agua", provider="agerh", organization="AGERH", dataset="bacias", product="seguranca_hidrica").tag_layer(tbl_b)
            results["AGERH - Bacias Hidrográficas"] = tbl_b

        if params.get("load_corpos", False):
            tbl_c = service.build_corpos_hidricos_table(loader.load_corpos_hidricos())
            DataProvenance(dimension="agua", provider="agerh", organization="AGERH", dataset="corpos_hidricos", product="seguranca_hidrica").tag_layer(tbl_c)
            results["AGERH - Corpos Hídricos"] = tbl_c

        return results
