# -*- coding: utf-8 -*-
"""
Camada de serviço AGERH.
Reutiliza os serviços validados de conexão, download e parsing das APIs AGERH.
"""

import sys
import os

# Adiciona o diretório raiz do plugin ao sys.path se necessário
plugin_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if plugin_root not in sys.path:
    sys.path.insert(0, plugin_root)

try:
    import agerh_service as _svc
except ImportError:
    from .... import agerh_service as _svc

# Exporta os elementos do serviço validado
URLS = _svc.URLS
CACHE_DIR = _svc.CACHE_DIR
clean_str = _svc.clean_str
to_float = _svc.to_float
to_int = _svc.to_int
fetch_url = _svc.fetch_url
AgerhDataLoader = _svc.AgerhDataLoader
build_pontos_coleta_layer = _svc.build_pontos_coleta_layer
build_outorgas_layer = _svc.build_outorgas_layer
build_dados_iqa_table = _svc.build_dados_iqa_table
build_interferencias_table = _svc.build_interferencias_table
build_bacias_table = _svc.build_bacias_table
build_corpos_hidricos_table = _svc.build_corpos_hidricos_table
apply_iqa_style = _svc.apply_iqa_style
apply_outorgas_style = _svc.apply_outorgas_style
save_layers_to_geopackage = _svc.save_layers_to_geopackage
