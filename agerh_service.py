# -*- coding: utf-8 -*-
"""
Módulo de serviço para download, processamento e conversão dos dados
da Agência Estadual de Recursos Hídricos (AGERH - ES).
"""

import os
import sys
import ssl
import json
import tempfile
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsVectorFileWriter,
    QgsProject,
    QgsLayerTreeGroup,
    QgsCategorizedSymbolRenderer,
    QgsRendererCategory,
    QgsSymbol,
    QgsMarkerSymbol,
    QgsSimpleMarkerSymbolLayerBase
)
from qgis.PyQt.QtCore import QObject, pyqtSignal, QThread
from qgis.PyQt.QtGui import QColor

try:
    from qgis.PyQt.QtCore import QMetaType
    FIELD_STRING = QMetaType.Type.QString
    FIELD_DOUBLE = QMetaType.Type.Double
    FIELD_INT = QMetaType.Type.Int
except (ImportError, AttributeError):
    from qgis.PyQt.QtCore import QVariant
    FIELD_STRING = QVariant.String
    FIELD_DOUBLE = QVariant.Double
    FIELD_INT = QVariant.Int


URLS = {
    "pontos_coleta": "https://hidro.agerh.es.gov.br/exportar_iqa?type=pontos_coleta",
    "dados_iqa": "https://hidro.agerh.es.gov.br/exportar_iqa?type=dados_iqa",
    "corpos_hidricos": "https://hidro.agerh.es.gov.br/exportar_iqa?type=corpos_hidricos",
    "bacias": "https://hidro.agerh.es.gov.br/exportar_iqa?type=bacias",
    "outorgas": "https://hidro.agerh.es.gov.br/exportar_outorga?type=outorgas",
    "interferencias": "https://hidro.agerh.es.gov.br/exportar_outorga?type=interferencias",
}

CACHE_DIR = os.path.join(tempfile.gettempdir(), "agerh_qgis_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def clean_str(val):
    if val is None:
        return ""
    return str(val).strip().replace("\r\n", " ").replace("\r", " ").replace("\n", " ")


def to_float(val, default=None):
    if val is None:
        return default
    s = str(val).strip().replace(",", ".")
    if not s or s == "" or s.lower() == "none" or s == "-0.1" or s == "-0.05":
        # Note: In AGERH data, -0.1 or -0.05 are often below detection limit (LD/LQ)
        if s in ("-0.1", "-0.05"):
            return 0.0
        return default
    try:
        return float(s)
    except (ValueError, TypeError):
        return default


def to_int(val, default=None):
    if val is None:
        return default
    s = str(val).strip()
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default


def fetch_url(url, cache_key=None, force_refresh=False, timeout=60):
    """
    Baixa o conteúdo de uma URL, utilizando cache local se disponível.
    """
    cache_file = None
    if cache_key:
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.xml")
        if not force_refresh and os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    return f.read()
            except Exception:
                pass

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AGERH-QGIS-Plugin/1.0"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        content = resp.read()

    if cache_file:
        try:
            with open(cache_file, "wb") as f:
                f.write(content)
        except Exception:
            pass

    return content


class AgerhDataLoader:
    """
    Classe para carregar e converter os dados da AGERH em camadas QGIS.
    """

    def __init__(self, force_refresh=False):
        self.force_refresh = force_refresh

    def load_pontos_coleta(self, filter_situacao=None, filter_municipio=None, filter_bacia=None):
        raw = fetch_url(URLS["pontos_coleta"], "pontos_coleta", self.force_refresh)
        root = ET.fromstring(raw)
        records = []
        for p in root.findall("ponto"):
            d = p.find("dados")
            if d is not None:
                rec = {k: clean_str(v) for k, v in d.attrib.items()}
                # Aplica filtros
                if filter_situacao and filter_situacao != "Todos":
                    if rec.get("Situacao", "").lower() != filter_situacao.lower():
                        continue
                if filter_municipio and filter_municipio != "Todos":
                    if rec.get("Municipio", "").lower() != filter_municipio.lower():
                        continue
                if filter_bacia and filter_bacia != "Todas":
                    b = rec.get("Bacia", "").lower()
                    fb = filter_bacia.lower()
                    if fb not in b and b not in fb:
                        continue
                records.append(rec)
        return records

    def load_dados_iqa(self, filter_bacia=None):
        raw = fetch_url(URLS["dados_iqa"], "dados_iqa", self.force_refresh)
        root = ET.fromstring(raw)
        records = []
        for item in root.findall("dados_iqa"):
            d = item.find("dados")
            if d is not None:
                rec = {k: clean_str(v) for k, v in d.attrib.items()}
                if filter_bacia and filter_bacia != "Todas":
                    b = rec.get("bacia_hidrografica", "").lower()
                    fb = filter_bacia.lower()
                    if fb not in b and b not in fb:
                        continue
                records.append(rec)
        return records

    def load_outorgas(self, filter_municipio=None, filter_regiao=None, filter_status=None, filter_tipo=None):
        raw = fetch_url(URLS["outorgas"], "outorgas", self.force_refresh)
        root = ET.fromstring(raw)
        records = []
        for cad in root.findall("cadastro"):
            d = cad.find("dados")
            if d is not None:
                rec = {k: clean_str(v) for k, v in d.attrib.items()}
                # Filtros
                if filter_municipio and filter_municipio != "Todos":
                    if rec.get("nom_municipio", "").lower() != filter_municipio.lower():
                        continue
                if filter_regiao and filter_regiao != "Todas":
                    r = rec.get("nom_regiao_hidrografica", "").lower()
                    fr = filter_regiao.lower()
                    if fr not in r and r not in fr:
                        continue
                if filter_status and filter_status != "Todos":
                    if rec.get("status", "").lower() != filter_status.lower():
                        continue
                if filter_tipo and filter_tipo != "Todos":
                    if rec.get("tipo_de_in", "").lower() != filter_tipo.lower():
                        continue
                records.append(rec)
        return records

    def load_interferencias(self):
        raw = fetch_url(URLS["interferencias"], "interferencias", self.force_refresh, timeout=90)
        root = ET.fromstring(raw)
        records = []
        for item in root.findall("interferencia"):
            d = item.find("dados")
            if d is not None:
                rec = {k: clean_str(v) for k, v in d.attrib.items()}
                records.append(rec)
        return records

    def load_bacias(self):
        raw = fetch_url(URLS["bacias"], "bacias", self.force_refresh)
        root = ET.fromstring(raw)
        records = []
        for b in root.findall("bacia"):
            d = b.find("dados")
            if d is not None:
                records.append({k: clean_str(v) for k, v in d.attrib.items()})
        return records

    def load_corpos_hidricos(self):
        raw = fetch_url(URLS["corpos_hidricos"], "corpos_hidricos", self.force_refresh)
        root = ET.fromstring(raw)
        records = []
        for ch in root.findall("corpo_hidrico"):
            d = ch.find("dados")
            if d is not None:
                records.append({k: clean_str(v) for k, v in d.attrib.items()})
        return records


def build_pontos_coleta_layer(pontos_data, dados_iqa_records=None, enrich=True):
    """
    Cria uma camada de pontos QgsVectorLayer em EPSG:4326.
    Se enrich=True e dados_iqa_records for fornecido, anexa a última medição de IQA a cada ponto.
    """
    layer = QgsVectorLayer("Point?crs=EPSG:4326", "AGERH - Pontos de Coleta (IQA)", "memory")
    pr = layer.dataProvider()

    # Mapear última medição por estação (código AGERH)
    latest_iqa = {}
    if enrich and dados_iqa_records:
        for rec in dados_iqa_records:
            cd = rec.get("codigo_agerh", "").strip()
            if not cd:
                continue
            dt_str = rec.get("data_formatada", "") or rec.get("data_da_coleta", "")
            if cd not in latest_iqa:
                latest_iqa[cd] = rec
            else:
                prev_dt = latest_iqa[cd].get("data_formatada", "")
                if dt_str > prev_dt:
                    latest_iqa[cd] = rec

    fields = [
        QgsField("codigo", FIELD_STRING),
        QgsField("codigo_ana", FIELD_STRING),
        QgsField("corpo_hidrico", FIELD_STRING),
        QgsField("bacia", FIELD_STRING),
        QgsField("municipio", FIELD_STRING),
        QgsField("situacao", FIELD_STRING),
        QgsField("descricao", FIELD_STRING),
        QgsField("lat", FIELD_DOUBLE),
        QgsField("lng", FIELD_DOUBLE),
    ]

    if enrich and latest_iqa:
        fields.extend([
            QgsField("ultimo_iqa", FIELD_DOUBLE),
            QgsField("classe_iqa", FIELD_STRING),
            QgsField("data_coleta", FIELD_STRING),
            QgsField("ph", FIELD_DOUBLE),
            QgsField("oxigenio_dissolvido", FIELD_DOUBLE),
            QgsField("turbidez", FIELD_DOUBLE),
            QgsField("coliformes_termo", FIELD_DOUBLE),
            QgsField("fosforo_total", FIELD_DOUBLE),
            QgsField("nitrogenio_total", FIELD_DOUBLE),
            QgsField("dbo", FIELD_DOUBLE),
        ])

    pr.addAttributes(fields)
    layer.updateFields()

    features = []
    for item in pontos_data:
        lat = to_float(item.get("lat"))
        lng = to_float(item.get("lng"))
        if lat is None or lng is None:
            continue
        # Validação para território do Espírito Santo (~ -22 a -17 lat, -42 a -39 lng)
        if not (-23.0 <= lat <= -16.0 and -43.0 <= lng <= -38.0):
            continue

        feat = QgsFeature(layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lng, lat)))

        cd = item.get("Codigo", "")
        feat.setAttribute("codigo", cd)
        feat.setAttribute("codigo_ana", item.get("Codigo_ANA", ""))
        feat.setAttribute("corpo_hidrico", item.get("Corpo_hidrico", ""))
        feat.setAttribute("bacia", item.get("Bacia", ""))
        feat.setAttribute("municipio", item.get("Municipio", ""))
        feat.setAttribute("situacao", item.get("Situacao", ""))
        feat.setAttribute("descricao", item.get("Descricao", ""))
        feat.setAttribute("lat", lat)
        feat.setAttribute("lng", lng)

        if enrich and latest_iqa:
            meas = latest_iqa.get(cd)
            if meas:
                feat.setAttribute("ultimo_iqa", to_float(meas.get("iqa")))
                feat.setAttribute("classe_iqa", meas.get("classe_iqa", ""))
                feat.setAttribute("data_coleta", meas.get("data_formatada", "") or meas.get("data_da_coleta", ""))
                feat.setAttribute("ph", to_float(meas.get("ph")))
                feat.setAttribute("oxigenio_dissolvido", to_float(meas.get("oxigenio_dissolvido")))
                feat.setAttribute("turbidez", to_float(meas.get("turbidez")))
                feat.setAttribute("coliformes_termo", to_float(meas.get("coliformes_termotolerantes")))
                feat.setAttribute("fosforo_total", to_float(meas.get("fosforo_total")))
                feat.setAttribute("nitrogenio_total", to_float(meas.get("nitrogenio_total")))
                feat.setAttribute("dbo", to_float(meas.get("demanda_bioquimica_de_oxigenio")))

        features.append(feat)

    pr.addFeatures(features)
    layer.updateExtents()
    return layer


def build_outorgas_layer(outorgas_data, interferencias_records=None, enrich=True):
    """
    Cria uma camada de pontos QgsVectorLayer em EPSG:31984 (SIRGAS 2000 / UTM zone 24S).
    Se enrich=True e interferencias_records for fornecido, vincula resumo de vazões.
    """
    layer = QgsVectorLayer("Point?crs=EPSG:31984", "AGERH - Outorgas", "memory")
    pr = layer.dataProvider()

    interf_map = {}
    if enrich and interferencias_records:
        for item in interferencias_records:
            proc = item.get("num_processo", "").strip()
            if not proc:
                continue
            if proc not in interf_map:
                interf_map[proc] = item

    fields = [
        QgsField("no_process", FIELD_STRING),
        QgsField("status", FIELD_STRING),
        QgsField("nome_do_em", FIELD_STRING),
        QgsField("tipo_de_in", FIELD_STRING),
        QgsField("finalidade", FIELD_STRING),
        QgsField("modalidade", FIELD_STRING),
        QgsField("no_documen", FIELD_STRING),
        QgsField("dt_documen", FIELD_STRING),
        QgsField("dt_publica", FIELD_STRING),
        QgsField("dt_vencime", FIELD_STRING),
        QgsField("nom_municipio", FIELD_STRING),
        QgsField("nom_hidrografia_lin", FIELD_STRING),
        QgsField("nom_regiao_hidrografica", FIELD_STRING),
        QgsField("dt_entrada", FIELD_STRING),
        QgsField("dt_tramitacao", FIELD_STRING),
        QgsField("este", FIELD_DOUBLE),
        QgsField("norte", FIELD_DOUBLE),
    ]

    if enrich and interf_map:
        fields.extend([
            QgsField("tip_interferencia", FIELD_STRING),
            QgsField("status_interferencia", FIELD_STRING),
            QgsField("vazao_q90_ls", FIELD_DOUBLE),
            QgsField("vazao_qmedia_ls", FIELD_DOUBLE),
            QgsField("vazao_referencia_ls", FIELD_DOUBLE),
            QgsField("vazao_req_max_ls", FIELD_DOUBLE),
            QgsField("area_montante_m2", FIELD_DOUBLE),
        ])

    pr.addAttributes(fields)
    layer.updateFields()

    features = []
    for item in outorgas_data:
        este = to_float(item.get("este"))
        norte = to_float(item.get("norte"))
        if este is None or norte is None:
            continue
        # Validação UTM 24S ES: X entre ~150.000 e ~500.000, Y entre ~7.600.000 e ~8.100.000
        if not (150000 <= este <= 550000 and 7500000 <= norte <= 8200000):
            continue

        feat = QgsFeature(layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(este, norte)))

        proc = item.get("no_process", "")
        feat.setAttribute("no_process", proc)
        feat.setAttribute("status", item.get("status", ""))
        feat.setAttribute("nome_do_em", item.get("nome_do_em", ""))
        feat.setAttribute("tipo_de_in", item.get("tipo_de_in", ""))
        feat.setAttribute("finalidade", item.get("finalidade", ""))
        feat.setAttribute("modalidade", item.get("modalidade", ""))
        feat.setAttribute("no_documen", item.get("no_documen", ""))
        feat.setAttribute("dt_documen", item.get("dt_documen", ""))
        feat.setAttribute("dt_publica", item.get("dt_publica", ""))
        feat.setAttribute("dt_vencime", item.get("dt_vencime", ""))
        feat.setAttribute("nom_municipio", item.get("nom_municipio", ""))
        feat.setAttribute("nom_hidrografia_lin", item.get("nom_hidrografia_lin", ""))
        feat.setAttribute("nom_regiao_hidrografica", item.get("nom_regiao_hidrografica", ""))
        feat.setAttribute("dt_entrada", item.get("dt_entrada", ""))
        feat.setAttribute("dt_tramitacao", item.get("dt_tramitacao", ""))
        feat.setAttribute("este", este)
        feat.setAttribute("norte", norte)

        if enrich and interf_map:
            interf = interf_map.get(proc)
            if interf:
                feat.setAttribute("tip_interferencia", interf.get("tip_interferencia", ""))
                feat.setAttribute("status_interferencia", interf.get("dcr_status_interferencia", ""))
                feat.setAttribute("vazao_q90_ls", to_float(interf.get("vlr_vazao_q90_ls")))
                feat.setAttribute("vazao_qmedia_ls", to_float(interf.get("vlr_vazao_qmedia_ls")))
                feat.setAttribute("vazao_referencia_ls", to_float(interf.get("vlr_vazao_referencia_ls")))
                feat.setAttribute("area_montante_m2", to_float(interf.get("vlr_area_acumulada_montante_m2")))

                # Calcular vazão máxima mensal requerida
                vaz_max = 0.0
                for m in range(1, 13):
                    k = f"vlr_vazao_requerida_{m:02d}_ls"
                    v = to_float(interf.get(k), 0.0)
                    if v and v > vaz_max:
                        vaz_max = v
                feat.setAttribute("vazao_req_max_ls", vaz_max if vaz_max > 0 else None)

        features.append(feat)

    pr.addFeatures(features)
    layer.updateExtents()
    return layer


def build_dados_iqa_table(records):
    """
    Cria uma tabela não espacial QgsVectorLayer contendo o histórico de medições IQA.
    """
    layer = QgsVectorLayer("none", "AGERH - Histórico IQA", "memory")
    pr = layer.dataProvider()

    key_fields = [
        QgsField("id", FIELD_INT),
        QgsField("codigo_agerh", FIELD_STRING),
        QgsField("bacia_hidrografica", FIELD_STRING),
        QgsField("corpo_hidrico", FIELD_STRING),
        QgsField("campanha", FIELD_INT),
        QgsField("data_coleta", FIELD_STRING),
        QgsField("iqa", FIELD_DOUBLE),
        QgsField("classe_iqa", FIELD_STRING),
        QgsField("ph", FIELD_DOUBLE),
        QgsField("oxigenio_dissolvido", FIELD_DOUBLE),
        QgsField("turbidez", FIELD_DOUBLE),
        QgsField("dbo", FIELD_DOUBLE),
        QgsField("dqo", FIELD_DOUBLE),
        QgsField("coliformes_termo", FIELD_DOUBLE),
        QgsField("nitrogenio_total", FIELD_DOUBLE),
        QgsField("fosforo_total", FIELD_DOUBLE),
        QgsField("temperatura_agua", FIELD_DOUBLE),
        QgsField("temperatura_ar", FIELD_DOUBLE),
        QgsField("solidos_totais", FIELD_DOUBLE),
        QgsField("condutividade_eletrica", FIELD_DOUBLE),
        QgsField("cloreto_total", FIELD_DOUBLE),
        QgsField("chuva_24h", FIELD_STRING),
    ]
    pr.addAttributes(key_fields)
    layer.updateFields()

    features = []
    for r in records:
        feat = QgsFeature(layer.fields())
        feat.setAttribute("id", to_int(r.get("Id")))
        feat.setAttribute("codigo_agerh", r.get("codigo_agerh", ""))
        feat.setAttribute("bacia_hidrografica", r.get("bacia_hidrografica", ""))
        feat.setAttribute("corpo_hidrico", r.get("corpo_hidrico", ""))
        feat.setAttribute("campanha", to_int(r.get("campanha")))
        feat.setAttribute("data_coleta", r.get("data_formatada", "") or r.get("data_da_coleta", ""))
        feat.setAttribute("iqa", to_float(r.get("iqa")))
        feat.setAttribute("classe_iqa", r.get("classe_iqa", ""))
        feat.setAttribute("ph", to_float(r.get("ph")))
        feat.setAttribute("oxigenio_dissolvido", to_float(r.get("oxigenio_dissolvido")))
        feat.setAttribute("turbidez", to_float(r.get("turbidez")))
        feat.setAttribute("dbo", to_float(r.get("demanda_bioquimica_de_oxigenio")))
        feat.setAttribute("dqo", to_float(r.get("demanda_quimica_de_oxigenio")))
        feat.setAttribute("coliformes_termo", to_float(r.get("coliformes_termotolerantes")))
        feat.setAttribute("nitrogenio_total", to_float(r.get("nitrogenio_total")))
        feat.setAttribute("fosforo_total", to_float(r.get("fosforo_total")))
        feat.setAttribute("temperatura_agua", to_float(r.get("temperatura_da_amostra")))
        feat.setAttribute("temperatura_ar", to_float(r.get("temperatura_do_ar")))
        feat.setAttribute("solidos_totais", to_float(r.get("solidos_totais")))
        feat.setAttribute("condutividade_eletrica", to_float(r.get("condutividade_eletrica")))
        feat.setAttribute("cloreto_total", to_float(r.get("cloreto_total")))
        feat.setAttribute("chuva_24h", r.get("chuva_ultimas_24_h", ""))
        features.append(feat)

    pr.addFeatures(features)
    return layer


def build_interferencias_table(records):
    """
    Cria uma tabela não espacial QgsVectorLayer com os dados de interferência de outorgas.
    """
    layer = QgsVectorLayer("none", "AGERH - Interferências de Outorga", "memory")
    pr = layer.dataProvider()

    fields = [
        QgsField("num_processo", FIELD_STRING),
        QgsField("tip_interferencia", FIELD_STRING),
        QgsField("status", FIELD_STRING),
        QgsField("vazao_q90_ls", FIELD_DOUBLE),
        QgsField("vazao_qmedia_ls", FIELD_DOUBLE),
        QgsField("vazao_referencia_ls", FIELD_DOUBLE),
        QgsField("tip_vazao_referencia", FIELD_STRING),
        QgsField("area_montante_m2", FIELD_DOUBLE),
        QgsField("precipitacao_media_mm", FIELD_DOUBLE),
        QgsField("distancia_foz", FIELD_DOUBLE),
    ]
    # Adicionar colunas dos 12 meses de vazão requerida
    for m in range(1, 13):
        fields.append(QgsField(f"vazao_req_{m:02d}_ls", FIELD_DOUBLE))
        fields.append(QgsField(f"horas_dia_{m:02d}", FIELD_STRING))
        fields.append(QgsField(f"dias_mes_{m:02d}", FIELD_INT))

    pr.addAttributes(fields)
    layer.updateFields()

    features = []
    for r in records:
        feat = QgsFeature(layer.fields())
        feat.setAttribute("num_processo", r.get("num_processo", ""))
        feat.setAttribute("tip_interferencia", r.get("tip_interferencia", ""))
        feat.setAttribute("status", r.get("dcr_status_interferencia", ""))
        feat.setAttribute("vazao_q90_ls", to_float(r.get("vlr_vazao_q90_ls")))
        feat.setAttribute("vazao_qmedia_ls", to_float(r.get("vlr_vazao_qmedia_ls")))
        feat.setAttribute("vazao_referencia_ls", to_float(r.get("vlr_vazao_referencia_ls")))
        feat.setAttribute("tip_vazao_referencia", r.get("tip_vazao_referencia", ""))
        feat.setAttribute("area_montante_m2", to_float(r.get("vlr_area_acumulada_montante_m2")))
        feat.setAttribute("precipitacao_media_mm", to_float(r.get("vlr_precipitacao_media_mm")))
        feat.setAttribute("distancia_foz", to_float(r.get("vlr_distancia_foz")))

        for m in range(1, 13):
            feat.setAttribute(f"vazao_req_{m:02d}_ls", to_float(r.get(f"vlr_vazao_requerida_{m:02d}_ls")))
            feat.setAttribute(f"horas_dia_{m:02d}", r.get(f"tmp_horas_dia_uso_{m:02d}", ""))
            feat.setAttribute(f"dias_mes_{m:02d}", to_int(r.get(f"tmp_dias_mes_uso_{m:02d}")))

        features.append(feat)

    pr.addFeatures(features)
    return layer


def build_bacias_table(records):
    layer = QgsVectorLayer("none", "AGERH - Bacias Hidrográficas", "memory")
    pr = layer.dataProvider()
    pr.addAttributes([
        QgsField("id_bacia", FIELD_INT),
        QgsField("bacia_hidrografica", FIELD_STRING),
    ])
    layer.updateFields()
    features = []
    for r in records:
        feat = QgsFeature(layer.fields())
        feat.setAttribute("id_bacia", to_int(r.get("id_bacia")))
        feat.setAttribute("bacia_hidrografica", r.get("bacia_hidrografica_bh", ""))
        features.append(feat)
    pr.addFeatures(features)
    return layer


def build_corpos_hidricos_table(records):
    layer = QgsVectorLayer("none", "AGERH - Corpos Hídricos", "memory")
    pr = layer.dataProvider()
    pr.addAttributes([
        QgsField("id_corpo_hidrico", FIELD_INT),
        QgsField("corpo_hidrico", FIELD_STRING),
        QgsField("id_bacia", FIELD_INT),
    ])
    layer.updateFields()
    features = []
    for r in records:
        feat = QgsFeature(layer.fields())
        feat.setAttribute("id_corpo_hidrico", to_int(r.get("id_corpo_hidrico")))
        feat.setAttribute("corpo_hidrico", r.get("corpo_hidrico_ch", ""))
        feat.setAttribute("id_bacia", to_int(r.get("id_bacia")))
        features.append(feat)
    pr.addFeatures(features)
    return layer


def apply_iqa_style(layer):
    """
    Aplica estilo categorizado por classe de IQA nos pontos de coleta.
    """
    classes_cores = [
        ("Ótima", "#0066cc", "Ótima (IQA 80-100)"),
        ("Boa", "#33a02c", "Boa (IQA 52-79)"),
        ("Médio", "#fdbf6f", "Média (IQA 37-51)"),
        ("Ruim", "#ff7f00", "Ruim (IQA 20-36)"),
        ("Péssima", "#e31a1c", "Péssima (IQA 0-19)"),
        ("", "#999999", "Sem dados recentes"),
    ]
    categories = []
    for val, hex_color, label in classes_cores:
        sym = QgsMarkerSymbol.createSimple({
            "name": "circle",
            "color": hex_color,
            "size": "3.5",
            "outline_color": "#ffffff",
            "outline_width": "0.5",
        })
        cat = QgsRendererCategory(val, sym, label)
        categories.append(cat)

    renderer = QgsCategorizedSymbolRenderer("classe_iqa", categories)
    layer.setRenderer(renderer)
    layer.triggerRepaint()


def apply_outorgas_style(layer):
    """
    Aplica estilo categorizado por tipo de interferência nas outorgas.
    """
    tipos_cores = [
        ("Captação direta em corpo hídrico superficial", "#1f78b4", "Captação Superficial"),
        ("Captação direta em corpo hídrico subterrâneo", "#33a02c", "Captação Subterrânea"),
        ("Barramento com captação", "#00cccc", "Barramento c/ Captação"),
        ("Barramento sem captação", "#6666cc", "Barramento s/ Captação"),
        ("Lançamento de efluentes", "#e31a1c", "Lançamento de Efluentes"),
        ("Aquicultura", "#ff7f00", "Aquicultura"),
        ("Aproveitamento hidrelétrico maior que 1MW", "#6a3d9a", "Hidrelétrica > 1MW"),
        ("Aproveitamento hidrelétrico menor ou igual a 1MW", "#b15928", "PCH / CGH <= 1MW"),
    ]
    categories = []
    for val, hex_color, label in tipos_cores:
        sym = QgsMarkerSymbol.createSimple({
            "name": "diamond",
            "color": hex_color,
            "size": "3.0",
            "outline_color": "#ffffff",
            "outline_width": "0.4",
        })
        cat = QgsRendererCategory(val, sym, label)
        categories.append(cat)

    # Categoria padrão para outros tipos
    sym_other = QgsMarkerSymbol.createSimple({
        "name": "circle",
        "color": "#b2df8a",
        "size": "2.5",
        "outline_color": "#ffffff",
        "outline_width": "0.3",
    })
    categories.append(QgsRendererCategory("", sym_other, "Outros / Indefinido"))

    renderer = QgsCategorizedSymbolRenderer("tipo_de_in", categories)
    layer.setRenderer(renderer)
    layer.triggerRepaint()


def save_layers_to_geopackage(layers_dict, gpkg_path):
    """
    Salva uma lista/dicionário de camadas (espaciais e não-espaciais) em um arquivo GeoPackage.
    """
    ctx = QgsCoordinateTransformContext()
    created_first = False

    for layer_name, layer in layers_dict.items():
        if not layer or not layer.isValid():
            continue
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "GPKG"
        # Nome da camada na tabela interna do GPKG
        safe_name = layer_name.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("ç", "c").replace("ã", "a").replace("í", "i").replace("á", "a")
        opts.layerName = safe_name

        if not created_first:
            opts.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
            created_first = True
        else:
            opts.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

        res = QgsVectorFileWriter.writeAsVectorFormatV3(layer, gpkg_path, ctx, opts)
        # res é uma tupla (errorCode, newFilename, newLayer, errorMessage)
        if res[0] != QgsVectorFileWriter.NoError:
            raise RuntimeError(f"Erro ao salvar camada {layer_name} no GeoPackage: {res[3]}")

    return gpkg_path
