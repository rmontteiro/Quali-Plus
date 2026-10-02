# -*- coding: utf-8 -*-
"""
Diálogo da Interface Gráfica do Plugin AGERH Hidro Dados.
"""

import os
import tempfile
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QUrl
from qgis.PyQt.QtGui import QIcon, QFont, QDesktopServices, QColor
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QRadioButton,
    QComboBox, QGroupBox, QPushButton, QProgressBar, QTabWidget,
    QWidget, QFileDialog, QMessageBox, QFrame, QButtonGroup, QLineEdit,
    QGridLayout, QScrollArea
)
from qgis.core import (
    QgsProject, QgsLayerTreeGroup, QgsRectangle
)

from . import agerh_service

MUNICIPIOS_ES = [
    "Todos os Municípios (78)", "Afonso Cláudio", "Água Doce do Norte", "Águia Branca",
    "Alegre", "Alfredo Chaves", "Alto Rio Novo", "Anchieta", "Apiacá", "Aracruz",
    "Atílio Vivácqua", "Baixo Guandu", "Barra de São Francisco", "Boa Esperança",
    "Bom Jesus do Norte", "Brejetuba", "Cachoeiro de Itapemirim", "Cariacica",
    "Castelo", "Colatina", "Conceição da Barra", "Conceição do Castelo",
    "Divino de São Lourenço", "Domingos Martins", "Dores do Rio Preto", "Ecoporanga",
    "Fundão", "Governador Lindenberg", "Guaçuí", "Guarapari", "Ibatiba", "Ibiraçu",
    "Ibitirama", "Iconha", "Irupi", "Itaguaçu", "Itapemirim", "Itarana", "Iúna",
    "Jaguaré", "Jerônimo Monteiro", "João Neiva", "Laranja da Terra", "Linhares",
    "Mantenópolis", "Marataízes", "Marechal Floriano", "Marilândia", "Mimoso do Sul",
    "Montanha", "Mucurici", "Muniz Freire", "Muqui", "Nova Venécia", "Pancas",
    "Pedro Canário", "Pinheiros", "Piúma", "Ponto Belo", "Presidente Kennedy",
    "Rio Bananal", "Rio Novo do Sul", "Santa Leopoldina", "Santa Maria de Jetibá",
    "Santa Teresa", "São Domingos do Norte", "São Gabriel da Palha",
    "São José do Calçado", "São Mateus", "São Roque do Canaã", "Serra",
    "Sooretama", "Vargem Alta", "Venda Nova do Imigrante", "Viana",
    "Vila Pavão", "Vila Valério", "Vila Velha", "Vitória"
]

BACIAS_ES = [
    "Todas as Bacias", "Benevente", "Doce", "Guarapari", "Itabapoana",
    "Itapemirim", "Itaúnas", "Jucu", "Novo", "Reis Magos", "Riacho",
    "Santa Maria da Vitória", "São Mateus"
]

STATUS_OUTORGA = [
    "Todos", "Concluído", "Aguardando análise", "Em análise",
    "Certificado de Regularidade", "Incompleto", "Incompleto/Aguardando reanálise",
    "Indeferido", "Arquivado"
]

TIPOS_INTERFERENCIA = [
    "Todos",
    "Captação direta em corpo hídrico superficial",
    "Captação direta em corpo hídrico subterrâneo",
    "Barramento com captação",
    "Barramento sem captação",
    "Lançamento de efluentes",
    "Aquicultura",
    "Aproveitamento hidrelétrico maior que 1MW",
    "Aproveitamento hidrelétrico menor ou igual a 1MW",
    "Captação em barramento"
]


class AgerhWorker(QThread):
    progress_changed = pyqtSignal(int, str)
    finished_success = pyqtSignal(dict)
    finished_error = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            self.progress_changed.emit(5, "Iniciando conexão com APIs da AGERH...")
            loader = agerh_service.AgerhDataLoader(force_refresh=self.config.get("force_refresh", False))

            layers_to_load = {}
            dados_iqa_records = None
            interf_records = None

            # 1. Carregar IQA para enriquecimento se necessário
            need_iqa = self.config["chk_iqa_table"] or (
                self.config["chk_pontos"] and self.config["enrich_iqa"]
            )
            if need_iqa:
                self.progress_changed.emit(15, "Obtendo dados de monitoramento IQA...")
                dados_iqa_records = loader.load_dados_iqa(
                    filter_bacia=self.config["filter_bacia"] if self.config["filter_bacia"] != "Todas as Bacias" else None
                )

            # 2. Carregar Interferências para enriquecimento se necessário
            need_interf = self.config["chk_interf_table"] or (
                self.config["chk_outorgas"] and self.config["enrich_outorga"]
            )
            if need_interf:
                self.progress_changed.emit(30, "Obtendo dados de interferências e vazões outorgadas...")
                interf_records = loader.load_interferencias()

            # 3. Pontos de Coleta
            if self.config["chk_pontos"]:
                self.progress_changed.emit(50, "Processando pontos de coleta...")
                pontos_data = loader.load_pontos_coleta(
                    filter_situacao=self.config["filter_situacao"],
                    filter_municipio=self.config["filter_municipio"] if self.config["filter_municipio"] != "Todos os Municípios (78)" else None,
                    filter_bacia=self.config["filter_bacia"] if self.config["filter_bacia"] != "Todas as Bacias" else None
                )
                layer_pts = agerh_service.build_pontos_coleta_layer(
                    pontos_data,
                    dados_iqa_records=dados_iqa_records,
                    enrich=self.config["enrich_iqa"]
                )
                if self.config["auto_style"]:
                    agerh_service.apply_iqa_style(layer_pts)
                layers_to_load["AGERH - Pontos de Coleta (IQA)"] = layer_pts

            # 4. Outorgas
            if self.config["chk_outorgas"]:
                self.progress_changed.emit(65, "Processando outorgas de recursos hídricos...")
                outorgas_data = loader.load_outorgas(
                    filter_municipio=self.config["filter_municipio"] if self.config["filter_municipio"] != "Todos os Municípios (78)" else None,
                    filter_regiao=self.config["filter_bacia"] if self.config["filter_bacia"] != "Todas as Bacias" else None,
                    filter_status=self.config["filter_status"],
                    filter_tipo=self.config["filter_tipo"]
                )
                layer_out = agerh_service.build_outorgas_layer(
                    outorgas_data,
                    interferencias_records=interf_records,
                    enrich=self.config["enrich_outorga"]
                )
                if self.config["auto_style"]:
                    agerh_service.apply_outorgas_style(layer_out)
                layers_to_load["AGERH - Outorgas"] = layer_out

            # 5. Tabela Histórico IQA
            if self.config["chk_iqa_table"] and dados_iqa_records:
                self.progress_changed.emit(80, "Construindo tabela de medições IQA...")
                tbl_iqa = agerh_service.build_dados_iqa_table(dados_iqa_records)
                layers_to_load["AGERH - Histórico IQA"] = tbl_iqa

            # 6. Tabela Interferências
            if self.config["chk_interf_table"] and interf_records:
                self.progress_changed.emit(85, "Construindo tabela de interferências...")
                tbl_interf = agerh_service.build_interferencias_table(interf_records)
                layers_to_load["AGERH - Interferências"] = tbl_interf

            # 7. Bacias
            if self.config["chk_bacias"]:
                self.progress_changed.emit(90, "Carregando bacias hidrográficas...")
                bacias_data = loader.load_bacias()
                tbl_bacias = agerh_service.build_bacias_table(bacias_data)
                layers_to_load["AGERH - Bacias Hidrográficas"] = tbl_bacias

            # 8. Corpos Hídricos
            if self.config["chk_corpos"]:
                self.progress_changed.emit(95, "Carregando corpos hídricos...")
                corpos_data = loader.load_corpos_hidricos()
                tbl_corpos = agerh_service.build_corpos_hidricos_table(corpos_data)
                layers_to_load["AGERH - Corpos Hídricos"] = tbl_corpos

            # Exportação GPKG se solicitado
            if self.config["output_mode"] == "gpkg":
                gpkg_file = self.config["gpkg_path"]
                self.progress_changed.emit(98, f"Salvando em GeoPackage: {os.path.basename(gpkg_file)}...")
                agerh_service.save_layers_to_geopackage(layers_to_load, gpkg_file)

            self.progress_changed.emit(100, "Concluído com sucesso!")
            self.finished_success.emit(layers_to_load)

        except Exception as e:
            import traceback
            err_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.finished_error.emit(err_msg)


class AgerhDialog(QDialog):
    """
    Janela principal para consulta e carregamento dos dados da AGERH no QGIS.
    """

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.worker = None

        self.setWindowTitle("AGERH Hidro Dados - Recursos Hídricos do Espírito Santo")
        self.setMinimumSize(620, 580)
        self.resize(650, 600)

        # Ícone da janela
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Header elegante
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #005c8a, stop:1 #003355);
                border-radius: 6px;
                padding: 10px;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 6, 8, 6)

        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(48, 48))
        h_layout.addWidget(icon_label)

        v_titles = QVBoxLayout()
        v_titles.setSpacing(2)
        lbl_title = QLabel("AGERH Hidro Dados • Espírito Santo")
        lbl_title.setStyleSheet("font-size: 15pt; font-weight: bold; color: #ffffff;")
        lbl_sub = QLabel("Agência Estadual de Recursos Hídricos • Qualidade da Água & Outorgas")
        lbl_sub.setStyleSheet("font-size: 9pt; color: #bde0fe;")
        v_titles.addWidget(lbl_title)
        v_titles.addWidget(lbl_sub)
        h_layout.addLayout(v_titles)
        h_layout.addStretch()

        main_layout.addWidget(header)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tab_camadas = QWidget()
        self.tab_filtros = QWidget()
        self.tab_saida = QWidget()
        self.tab_sobre = QWidget()

        self.setup_tab_camadas()
        self.setup_tab_filtros()
        self.setup_tab_saida()
        self.setup_tab_sobre()

        self.tabs.addTab(self.tab_camadas, "1. Camadas & Tabelas")
        self.tabs.addTab(self.tab_filtros, "2. Filtros")
        self.tabs.addTab(self.tab_saida, "3. Destino & Estilo")
        self.tabs.addTab(self.tab_sobre, "4. Sobre & APIs")

        main_layout.addWidget(self.tabs)

        # Barra de Progresso e Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("Selecione as camadas desejadas e clique em 'Carregar no QGIS'.")
        self.lbl_status.setStyleSheet("color: #495057; font-size: 9pt;")
        main_layout.addWidget(self.lbl_status)

        # Botões inferiores
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_carregar = QPushButton("  Carregar Dados no QGIS")
        self.btn_carregar.setIcon(self.windowIcon())
        self.btn_carregar.setStyleSheet("""
            QPushButton {
                background-color: #0077b6;
                color: white;
                font-weight: bold;
                font-size: 10pt;
                padding: 8px 18px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #023e8a;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
            }
        """)
        self.btn_carregar.clicked.connect(self.on_carregar_clicked)

        self.btn_fechar = QPushButton("Fechar")
        self.btn_fechar.setStyleSheet("padding: 8px 16px;")
        self.btn_fechar.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_carregar)
        btn_layout.addWidget(self.btn_fechar)

        main_layout.addLayout(btn_layout)

    def setup_tab_camadas(self):
        layout = QVBoxLayout(self.tab_camadas)
        layout.setSpacing(10)

        # Grupo Camadas Espaciais
        grp_espaciais = QGroupBox("Camadas Espaciais (Vetores de Pontos)")
        v_esp = QVBoxLayout(grp_espaciais)

        self.chk_pontos = QCheckBox("Pontos de Coleta IQA - Qualidade da Água (WGS 84 - EPSG:4326)")
        self.chk_pontos.setChecked(True)
        self.chk_pontos.setStyleSheet("font-weight: bold; color: #023e8a;")

        self.chk_outorgas = QCheckBox("Outorgas de Recursos Hídricos (SIRGAS 2000 / UTM 24S - EPSG:31984)")
        self.chk_outorgas.setChecked(True)
        self.chk_outorgas.setStyleSheet("font-weight: bold; color: #023e8a;")

        v_esp.addWidget(self.chk_pontos)
        v_esp.addWidget(self.chk_outorgas)
        layout.addWidget(grp_espaciais)

        # Grupo Tabelas Não-Espaciais
        grp_tabelas = QGroupBox("Tabelas Complementares (Atributos / Séries)")
        v_tab = QVBoxLayout(grp_tabelas)

        self.chk_iqa_table = QCheckBox("Histórico Completo de Medições IQA (~1.800 coletas c/ 53 parâmetros físico-químicos)")
        self.chk_interf_table = QCheckBox("Tabela Detalhada de Interferências (~10.000 registros c/ vazões mensais e balanço)")
        self.chk_bacias = QCheckBox("Bacias Hidrográficas Cadastradas (12 bacias)")
        self.chk_corpos = QCheckBox("Corpos Hídricos Cadastrados (59 rios e lagoas)")

        v_tab.addWidget(self.chk_iqa_table)
        v_tab.addWidget(self.chk_interf_table)
        v_tab.addWidget(self.chk_bacias)
        v_tab.addWidget(self.chk_corpos)
        layout.addWidget(grp_tabelas)

        # Grupo Enriquecimento Inteligente
        grp_enrich = QGroupBox("Enriquecimento Automático das Camadas")
        v_enr = QVBoxLayout(grp_enrich)

        self.chk_enrich_iqa = QCheckBox("Vincular última medição de IQA aos Pontos de Coleta (permite colorir por qualidade da água)")
        self.chk_enrich_iqa.setChecked(True)

        self.chk_enrich_outorga = QCheckBox("Vincular dados de vazão (Q90, Qmédia, Vazão Requerida) aos Pontos de Outorga")
        self.chk_enrich_outorga.setChecked(True)

        v_enr.addWidget(self.chk_enrich_iqa)
        v_enr.addWidget(self.chk_enrich_outorga)
        layout.addWidget(grp_enrich)

        layout.addStretch()

    def setup_tab_filtros(self):
        layout = QVBoxLayout(self.tab_filtros)
        layout.setSpacing(10)

        grp_filtros = QGroupBox("Filtros Espaciais e Temáticos")
        grid = QGridLayout(grp_filtros)
        grid.setSpacing(8)

        # Município
        lbl_mun = QLabel("Município (ES):")
        self.cmb_municipio = QComboBox()
        self.cmb_municipio.addItems(MUNICIPIOS_ES)
        grid.addWidget(lbl_mun, 0, 0)
        grid.addWidget(self.cmb_municipio, 0, 1)

        # Bacia
        lbl_bacia = QLabel("Bacia Hidrográfica:")
        self.cmb_bacia = QComboBox()
        self.cmb_bacia.addItems(BACIAS_ES)
        grid.addWidget(lbl_bacia, 1, 0)
        grid.addWidget(self.cmb_bacia, 1, 1)

        # Status da Outorga
        lbl_status = QLabel("Status da Outorga:")
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(STATUS_OUTORGA)
        grid.addWidget(lbl_status, 2, 0)
        grid.addWidget(self.cmb_status, 2, 1)

        # Tipo de Interferência
        lbl_tipo = QLabel("Tipo de Interferência:")
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(TIPOS_INTERFERENCIA)
        grid.addWidget(lbl_tipo, 3, 0)
        grid.addWidget(self.cmb_tipo, 3, 1)

        # Situação Ponto IQA
        lbl_sit = QLabel("Situação dos Pontos IQA:")
        self.cmb_situacao = QComboBox()
        self.cmb_situacao.addItems(["Todos", "Ativo", "Inativo"])
        grid.addWidget(lbl_sit, 4, 0)
        grid.addWidget(self.cmb_situacao, 4, 1)

        layout.addWidget(grp_filtros)

        btn_reset_filtros = QPushButton("Limpar Filtros (Restaurar Todos)")
        btn_reset_filtros.clicked.connect(self.reset_filtros)
        layout.addWidget(btn_reset_filtros)

        lbl_hint = QLabel(
            "💡 Dica: Aplicar filtros reduz significativamente o tempo de processamento "
            "e foca a análise na sua área de interesse."
        )
        lbl_hint.setWordWrap(True)
        lbl_hint.setStyleSheet("color: #6c757d; font-style: italic; font-size: 8.5pt;")
        layout.addWidget(lbl_hint)

        layout.addStretch()

    def reset_filtros(self):
        self.cmb_municipio.setCurrentIndex(0)
        self.cmb_bacia.setCurrentIndex(0)
        self.cmb_status.setCurrentIndex(0)
        self.cmb_tipo.setCurrentIndex(0)
        self.cmb_situacao.setCurrentIndex(0)

    def setup_tab_saida(self):
        layout = QVBoxLayout(self.tab_saida)
        layout.setSpacing(10)

        # Modo de Armazenamento
        grp_dest = QGroupBox("Destino dos Dados")
        v_dest = QVBoxLayout(grp_dest)

        self.rad_memory = QRadioButton("Carregar como Camadas em Memória (Rápido, temporário no projeto)")
        self.rad_memory.setChecked(True)
        self.rad_gpkg = QRadioButton("Salvar e Carregar a partir de GeoPackage (.gpkg)")

        self.btn_group_dest = QButtonGroup()
        self.btn_group_dest.addButton(self.rad_memory)
        self.btn_group_dest.addButton(self.rad_gpkg)
        self.rad_gpkg.toggled.connect(self.on_gpkg_toggled)

        v_dest.addWidget(self.rad_memory)
        v_dest.addWidget(self.rad_gpkg)

        # File picker GPKG
        h_gpkg = QHBoxLayout()
        self.txt_gpkg_path = QLineEdit()
        self.txt_gpkg_path.setPlaceholderText("Selecione o caminho do arquivo .gpkg...")
        self.txt_gpkg_path.setEnabled(False)

        self.btn_browse_gpkg = QPushButton("Procurar...")
        self.btn_browse_gpkg.setEnabled(False)
        self.btn_browse_gpkg.clicked.connect(self.browse_gpkg)

        h_gpkg.addWidget(self.txt_gpkg_path)
        h_gpkg.addWidget(self.btn_browse_gpkg)
        v_dest.addLayout(h_gpkg)

        layout.addWidget(grp_dest)

        # Estilo e Visualização
        grp_vis = QGroupBox("Opções de Visualização no QGIS")
        v_vis = QVBoxLayout(grp_vis)

        self.chk_auto_style = QCheckBox("Aplicar Estilização Temática Automática (Cores por classe IQA e tipo de outorga)")
        self.chk_auto_style.setChecked(True)

        self.chk_create_group = QCheckBox("Organizar camadas em Grupo no painel ('AGERH - Recursos Hídricos')")
        self.chk_create_group.setChecked(True)

        self.chk_zoom_extent = QCheckBox("Ajustar Zoom do mapa à extensão dos dados carregados")
        self.chk_zoom_extent.setChecked(True)

        v_vis.addWidget(self.chk_auto_style)
        v_vis.addWidget(self.chk_create_group)
        v_vis.addWidget(self.chk_zoom_extent)
        layout.addWidget(grp_vis)

        # Cache
        grp_cache = QGroupBox("Gerenciamento de Rede e Cache")
        v_cache = QVBoxLayout(grp_cache)

        self.chk_force_refresh = QCheckBox("Forçar download da internet (ignorar cache local)")
        self.chk_force_refresh.setChecked(False)

        lbl_cache_info = QLabel(f"Diretório de cache local: {agerh_service.CACHE_DIR}")
        lbl_cache_info.setStyleSheet("font-size: 8pt; color: #6c757d;")
        lbl_cache_info.setWordWrap(True)

        v_cache.addWidget(self.chk_force_refresh)
        v_cache.addWidget(lbl_cache_info)
        layout.addWidget(grp_cache)

        layout.addStretch()

    def on_gpkg_toggled(self, checked):
        self.txt_gpkg_path.setEnabled(checked)
        self.btn_browse_gpkg.setEnabled(checked)
        if checked and not self.txt_gpkg_path.text().strip():
            default_dir = os.path.expanduser("~")
            self.txt_gpkg_path.setText(os.path.join(default_dir, "agerh_dados_es.gpkg"))

    def browse_gpkg(self):
        fpath, _ = QFileDialog.getSaveFileName(
            self, "Salvar Camadas AGERH em GeoPackage",
            self.txt_gpkg_path.text().strip() or os.path.join(os.path.expanduser("~"), "agerh_dados_es.gpkg"),
            "GeoPackage (*.gpkg)"
        )
        if fpath:
            if not fpath.lower().endswith(".gpkg"):
                fpath += ".gpkg"
            self.txt_gpkg_path.setText(fpath)

    def setup_tab_sobre(self):
        layout = QVBoxLayout(self.tab_sobre)
        layout.setSpacing(10)

        lbl_desc = QLabel(
            "<h3>Plugin AGERH Hidro Dados</h3>"
            "<p>Este complemento conecta o <b>QGIS</b> aos serviços oficiais de dados abertos da "
            "<b>Agência Estadual de Recursos Hídricos do Espírito Santo (AGERH)</b>.</p>"
            "<p><b>Endpoints integrados:</b></p>"
            "<ul>"
            "<li><b>Pontos de Coleta IQA:</b> Rede de monitoramento da qualidade da água (EPSG:4326).</li>"
            "<li><b>Dados IQA:</b> Séries com pH, oxigênio dissolvido, turbidez, coliformes, DBO, IQA, etc.</li>"
            "<li><b>Outorgas:</b> Cadastros de concessão e direito de uso da água (EPSG:31984 - UTM 24S).</li>"
            "<li><b>Interferências:</b> Balanço hídrico, vazões requeridas mensais, Q90 e Qmédia.</li>"
            "<li><b>Bacias & Corpos Hídricos:</b> Tabelas de referência estadual.</li>"
            "</ul>"
            "<p><b>Referencial Geodésico:</b><br>"
            "• Coordenadas IQA em WGS 84 (EPSG:4326)<br>"
            "• Coordenadas Outorgas em SIRGAS 2000 / UTM Zona 24S (EPSG:31984)</p>"
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setOpenExternalLinks(True)
        layout.addWidget(lbl_desc)

        btn_portal = QPushButton("🌐 Abrir Portal Hidro AGERH no Navegador")
        btn_portal.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://hidro.agerh.es.gov.br")))
        layout.addWidget(btn_portal)

        layout.addStretch()

    def get_config(self):
        return {
            "chk_pontos": self.chk_pontos.isChecked(),
            "chk_outorgas": self.chk_outorgas.isChecked(),
            "chk_iqa_table": self.chk_iqa_table.isChecked(),
            "chk_interf_table": self.chk_interf_table.isChecked(),
            "chk_bacias": self.chk_bacias.isChecked(),
            "chk_corpos": self.chk_corpos.isChecked(),
            "enrich_iqa": self.chk_enrich_iqa.isChecked(),
            "enrich_outorga": self.chk_enrich_outorga.isChecked(),
            "filter_municipio": self.cmb_municipio.currentText(),
            "filter_bacia": self.cmb_bacia.currentText(),
            "filter_status": self.cmb_status.currentText(),
            "filter_tipo": self.cmb_tipo.currentText(),
            "filter_situacao": self.cmb_situacao.currentText(),
            "output_mode": "gpkg" if self.rad_gpkg.isChecked() else "memory",
            "gpkg_path": self.txt_gpkg_path.text().strip(),
            "auto_style": self.chk_auto_style.isChecked(),
            "create_group": self.chk_create_group.isChecked(),
            "zoom_extent": self.chk_zoom_extent.isChecked(),
            "force_refresh": self.chk_force_refresh.isChecked(),
        }

    def on_carregar_clicked(self):
        config = self.get_config()

        # Validações
        if not (config["chk_pontos"] or config["chk_outorgas"] or config["chk_iqa_table"] or
                config["chk_interf_table"] or config["chk_bacias"] or config["chk_corpos"]):
            QMessageBox.warning(self, "Aviso", "Selecione ao menos uma camada ou tabela para carregar!")
            return

        if config["output_mode"] == "gpkg":
            if not config["gpkg_path"]:
                QMessageBox.warning(self, "Aviso", "Por favor, especifique o caminho do arquivo GeoPackage (.gpkg)!")
                self.tabs.setCurrentIndex(2)
                return

        # Desabilita botões e inicia thread
        self.btn_carregar.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(5)
        self.lbl_status.setText("Conectando aos servidores da AGERH...")

        self.worker = AgerhWorker(config)
        self.worker.progress_changed.connect(self.on_worker_progress)
        self.worker.finished_success.connect(self.on_worker_success)
        self.worker.finished_error.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_progress(self, val, msg):
        self.progress_bar.setValue(val)
        self.lbl_status.setText(msg)

    def on_worker_success(self, layers_dict):
        self.btn_carregar.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.lbl_status.setText(f"Sucesso! {len(layers_dict)} camada(s) processada(s).")

        config = self.get_config()
        proj = QgsProject.instance()

        # Criar grupo no painel se solicitado
        group = None
        if config["create_group"]:
            root = proj.layerTreeRoot()
            group_name = "AGERH - Recursos Hídricos"
            group = root.findGroup(group_name)
            if not group:
                group = root.addGroup(group_name)

        combined_extent = QgsRectangle()
        first_extent = True

        for layer_name, layer in layers_dict.items():
            if not layer or not layer.isValid():
                continue

            # Se modo GPKG, carregar a partir do GPKG
            final_layer = layer
            if config["output_mode"] == "gpkg":
                safe_name = layer_name.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("ç", "c").replace("ã", "a").replace("í", "i").replace("á", "a")
                gpkg_uri = f"{config['gpkg_path']}|layername={safe_name}"
                from qgis.core import QgsVectorLayer
                final_layer = QgsVectorLayer(gpkg_uri, layer_name, "ogr")
                if config["auto_style"]:
                    if "Pontos de Coleta" in layer_name:
                        agerh_service.apply_iqa_style(final_layer)
                    elif "Outorgas" in layer_name:
                        agerh_service.apply_outorgas_style(final_layer)

            # Adicionar camada ao projeto
            proj.addMapLayer(final_layer, addToLegend=False)
            if group:
                group.addLayer(final_layer)
            else:
                proj.layerTreeRoot().addLayer(final_layer)

            if final_layer.isSpatial() and not final_layer.extent().isEmpty():
                if first_extent:
                    combined_extent = QgsRectangle(final_layer.extent())
                    first_extent = False
                else:
                    combined_extent.combineExtentWith(final_layer.extent())

        # Zoom na extensão se solicitado
        if config["zoom_extent"] and self.iface and not combined_extent.isEmpty():
            try:
                canvas = self.iface.mapCanvas()
                canvas.setExtent(combined_extent)
                canvas.refresh()
            except Exception:
                pass

        total_features = sum(l.featureCount() for l in layers_dict.values() if l and l.isValid())
        msg = f"Foram carregadas com sucesso {len(layers_dict)} camada(s) com um total de {total_features:,} registros!"
        if config["output_mode"] == "gpkg":
            msg += f"\n\nGeoPackage gerado em:\n{config['gpkg_path']}"

        QMessageBox.information(self, "AGERH Hidro Dados", msg)

    def on_worker_error(self, err_msg):
        self.btn_carregar.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.lbl_status.setText("Erro durante o processamento.")
        QMessageBox.critical(self, "Erro ao carregar dados da AGERH", f"Ocorreu um erro:\n\n{err_msg}")
