# -*- coding: utf-8 -*-
"""
Interface Gráfica do Módulo Água do QUALI+.
Apresenta a visão agregadora da dimensão ÁGUA com conectores estaduais, nacionais e globais,
distinguindo dimensões, fontes e produtos analíticos.
"""

import os
from datetime import datetime
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QIcon, QFont, QColor, QDesktopServices
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QGroupBox, QComboBox, QTextEdit, QProgressBar,
    QMessageBox, QFrame, QRadioButton, QButtonGroup, QCheckBox,
    QLineEdit, QFileDialog, QSplitter
)
from qgis.core import QgsProject, QgsRectangle, QgsVectorLayer

from ..base import ProviderStatus
from ..registry import SourceRegistry, ProductRegistry
from ..providers.agerh.adapter import AgerhProvider
from ..providers.agerh.worker import AgerhWorker
from ..providers.agerh import service as agerh_svc

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


class QualiAguaDialog(QDialog):
    """
    Diálogo principal da Dimensão Água do QUALI+.
    """

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.worker = None

        self.setWindowTitle("QUALI+ • Dimensão Temática ÁGUA")
        self.setMinimumSize(850, 680)
        self.resize(920, 720)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(10)

        # 1. Header institucional QUALI+
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f2b48, stop:0.5 #17426c, stop:1 #0077b6);
                border-radius: 6px;
                padding: 10px;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 6, 10, 6)

        v_titles = QVBoxLayout()
        v_titles.setSpacing(2)
        lbl_brand = QLabel("QUALI+ • Plataforma de Inteligência Territorial")
        lbl_brand.setStyleSheet("font-size: 10pt; color: #90e0ef; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;")
        lbl_title = QLabel("Dimensão Temática: ÁGUA")
        lbl_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #ffffff;")
        lbl_sub = QLabel("Integração federada de dados hidrológicos, qualidade da água, outorgas e extremos climáticos")
        lbl_sub.setStyleSheet("font-size: 9pt; color: #e0f2fe;")
        v_titles.addWidget(lbl_brand)
        v_titles.addWidget(lbl_title)
        v_titles.addWidget(lbl_sub)
        h_layout.addLayout(v_titles)
        h_layout.addStretch()

        badge_frame = QFrame()
        badge_frame.setStyleSheet("background: rgba(255, 255, 255, 0.15); border-radius: 4px; padding: 6px;")
        b_layout = QVBoxLayout(badge_frame)
        b_layout.setSpacing(2)
        lbl_b1 = QLabel("Módulo: ÁGUA v1.0")
        lbl_b1.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 8.5pt;")
        lbl_b2 = QLabel("SEAMA / AGERH - ES")
        lbl_b2.setStyleSheet("color: #caf0f8; font-size: 8pt;")
        b_layout.addWidget(lbl_b1)
        b_layout.addWidget(lbl_b2)
        h_layout.addWidget(badge_frame)

        main_layout.addWidget(header)

        # 2. Tabs do Módulo Água
        self.tabs = QTabWidget()
        self.tab_matrix = QWidget()
        self.tab_agerh = QWidget()
        self.tab_roadmap = QWidget()
        self.tab_provenance = QWidget()

        self.setup_tab_matrix()
        self.setup_tab_agerh()
        self.setup_tab_roadmap()
        self.setup_tab_provenance()

        self.tabs.addTab(self.tab_matrix, "1. Matriz de Fontes & Produtos")
        self.tabs.addTab(self.tab_agerh, "2. Conector Operacional AGERH (Disponível)")
        self.tabs.addTab(self.tab_roadmap, "3. Fontes Planejadas (Roadmap)")
        self.tabs.addTab(self.tab_provenance, "4. Proveniência & Auditoria")

        main_layout.addWidget(self.tabs)

        # 3. Rodapé com Botão Fechar
        footer_layout = QHBoxLayout()
        lbl_hint = QLabel("💡 A dimensão ÁGUA agrega dados estaduais (AGERH, AlertaES), nacionais (ANA, SGB, Cemaden) e globais (GloFAS, NASA, Sentinel).")
        lbl_hint.setStyleSheet("color: #64748b; font-size: 8.5pt; font-style: italic;")
        footer_layout.addWidget(lbl_hint)
        footer_layout.addStretch()

        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet("padding: 6px 18px;")
        btn_close.clicked.connect(self.reject)
        footer_layout.addWidget(btn_close)

        main_layout.addLayout(footer_layout)

    # =========================================================================
    # ABA 1: MATRIZ DE FONTES & PRODUTOS
    # =========================================================================
    def setup_tab_matrix(self):
        layout = QVBoxLayout(self.tab_matrix)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Barra de Filtros da Matriz
        h_filters = QHBoxLayout()
        h_filters.addWidget(QLabel("Filtrar por Produto:"))
        self.cmb_prod_filter = QComboBox()
        self.cmb_prod_filter.addItem("Todos os Produtos")
        for prod in ProductRegistry.list_all():
            self.cmb_prod_filter.addItem(f"{prod.name} ({prod.category})", prod.id)
        self.cmb_prod_filter.currentIndexChanged.connect(self.refresh_sources_table)
        h_filters.addWidget(self.cmb_prod_filter)

        h_filters.addWidget(QLabel("Filtrar por Status:"))
        self.cmb_status_filter = QComboBox()
        self.cmb_status_filter.addItems(["Todos os Status", "Apenas Disponíveis", "Planejados"])
        self.cmb_status_filter.currentIndexChanged.connect(self.refresh_sources_table)
        h_filters.addWidget(self.cmb_status_filter)

        h_filters.addStretch()
        layout.addLayout(h_filters)

        # Tabela de Fontes
        self.table_sources = QTableWidget()
        self.table_sources.setColumnCount(5)
        self.table_sources.setHorizontalHeaderLabels([
            "Fonte / Conector", "Organização", "Escopo", "Produtos Associados", "Status no QUALI+"
        ])
        self.table_sources.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_sources.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_sources.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_sources.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_sources.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_sources.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_sources.setSelectionMode(QTableWidget.SingleSelection)
        self.table_sources.itemSelectionChanged.connect(self.on_source_selected)
        layout.addWidget(self.table_sources)

        # Card de Detalhes da Fonte Selecionada
        self.grp_detail = QGroupBox("Detalhes da Fonte Selecionada")
        v_det = QVBoxLayout(self.grp_detail)
        v_det.setSpacing(6)

        self.lbl_det_title = QLabel("Selecione uma fonte na tabela acima para ver suas especificações.")
        self.lbl_det_title.setStyleSheet("font-weight: bold; font-size: 10pt; color: #0f172a;")
        self.lbl_det_desc = QLabel("")
        self.lbl_det_desc.setWordWrap(True)
        self.lbl_det_desc.setStyleSheet("color: #334155; font-size: 9pt;")

        h_actions = QHBoxLayout()
        self.btn_action_source = QPushButton("Abrir Conector Operacional AGERH")
        self.btn_action_source.setStyleSheet("""
            QPushButton {
                background-color: #0284c7; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #0369a1; }
        """)
        self.btn_action_source.clicked.connect(self.on_source_action_clicked)

        self.btn_web_source = QPushButton("🌐 Abrir Portal Oficial")
        self.btn_web_source.clicked.connect(self.on_open_source_web)

        h_actions.addWidget(self.btn_action_source)
        h_actions.addWidget(self.btn_web_source)
        h_actions.addStretch()

        v_det.addWidget(self.lbl_det_title)
        v_det.addWidget(self.lbl_det_desc)
        v_det.addLayout(h_actions)
        layout.addWidget(self.grp_detail)

        self.refresh_sources_table()

    def refresh_sources_table(self):
        selected_prod_id = self.cmb_prod_filter.currentData()
        status_filter = self.cmb_status_filter.currentText()

        sources = SourceRegistry.list_all()
        self.table_sources.setRowCount(0)

        for src in sources:
            # Filtro por produto
            if selected_prod_id and selected_prod_id not in src.get("products", []):
                continue

            # Filtro por status
            if status_filter == "Apenas Disponíveis" and src["status"] != ProviderStatus.AVAILABLE:
                continue
            if status_filter == "Planejados" and src["status"] != ProviderStatus.PLANNED:
                continue

            row = self.table_sources.rowCount()
            self.table_sources.insertRow(row)

            # 0. Nome
            it_name = QTableWidgetItem(src["name"])
            it_name.setData(Qt.UserRole, src["id"])
            it_name.setFont(QFont("Arial", 9, QFont.Bold))
            self.table_sources.setItem(row, 0, it_name)

            # 1. Organização
            self.table_sources.setItem(row, 1, QTableWidgetItem(src["organization"]))

            # 2. Escopo
            self.table_sources.setItem(row, 2, QTableWidgetItem(src["scope"]))

            # 3. Produtos
            prods_names = []
            for pid in src.get("products", []):
                p_obj = ProductRegistry.get(pid)
                if p_obj:
                    prods_names.append(p_obj.name)
            self.table_sources.setItem(row, 3, QTableWidgetItem(", ".join(prods_names)))

            # 4. Status
            if src["status"] == ProviderStatus.AVAILABLE:
                it_st = QTableWidgetItem("🟢 DISPONÍVEL (Operacional)")
                it_st.setForeground(QColor("#15803d"))
                it_st.setFont(QFont("Arial", 9, QFont.Bold))
            else:
                it_st = QTableWidgetItem("⏳ PLANEJADO (Roadmap)")
                it_st.setForeground(QColor("#475569"))
                it_st.setFont(QFont("Arial", 9))
            self.table_sources.setItem(row, 4, it_st)

        if self.table_sources.rowCount() > 0:
            self.table_sources.selectRow(0)

    def on_source_selected(self):
        rows = self.table_sources.selectedItems()
        if not rows:
            return
        src_id = self.table_sources.item(rows[0].row(), 0).data(Qt.UserRole)
        src = SourceRegistry.get(src_id)
        if not src:
            return

        self.current_selected_source = src
        self.lbl_det_title.setText(f"{src['name']} • {src['organization']} ({src['scope']})")
        self.lbl_det_desc.setText(f"{src['description']}\n\nProdutos Cobertos: {', '.join(src['products'])}")

        if src["status"] == ProviderStatus.AVAILABLE:
            self.btn_action_source.setText("⚡ Abrir Conector Operacional AGERH")
            self.btn_action_source.setEnabled(True)
        else:
            self.btn_action_source.setText("📋 Ver Especificação Técnica (Planejado)")
            self.btn_action_source.setEnabled(True)

    def on_source_action_clicked(self):
        if not hasattr(self, "current_selected_source"):
            return
        if self.current_selected_source["id"] == "agerh":
            self.tabs.setCurrentIndex(1)  # Vai para a aba do Conector AGERH
        else:
            self.tabs.setCurrentIndex(2)  # Vai para a aba de Roadmap

    def on_open_source_web(self):
        if hasattr(self, "current_selected_source") and self.current_selected_source.get("website"):
            QDesktopServices.openUrl(QUrl(self.current_selected_source["website"]))

    # =========================================================================
    # ABA 2: CONECTOR OPERACIONAL AGERH
    # =========================================================================
    def setup_tab_agerh(self):
        layout = QVBoxLayout(self.tab_agerh)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # Banner do Conector
        banner = QFrame()
        banner.setStyleSheet("background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px; padding: 8px;")
        b_layout = QHBoxLayout(banner)
        lbl_binfo = QLabel(
            "<b>Conector Operacional: AGERH / HidroAgerh</b> • "
            "Ingestão direta via <code>AgerhProvider (Adapter)</code> com rastreabilidade (DataProvenance)."
        )
        lbl_binfo.setStyleSheet("color: #0369a1; font-size: 9pt;")
        b_layout.addWidget(lbl_binfo)
        layout.addWidget(banner)

        # Camadas e Tabelas
        h_top = QHBoxLayout()

        grp_layers = QGroupBox("Camadas Espaciais & Tabelas AGERH")
        v_l = QVBoxLayout(grp_layers)
        self.chk_pontos = QCheckBox("Pontos de Coleta IQA - Qualidade da Água (EPSG:4326)")
        self.chk_pontos.setChecked(True)
        self.chk_pontos.setStyleSheet("font-weight: bold; color: #0284c7;")

        self.chk_outorgas = QCheckBox("Outorgas de Recursos Hídricos (SIRGAS 2000 UTM 24S - EPSG:31984)")
        self.chk_outorgas.setChecked(True)
        self.chk_outorgas.setStyleSheet("font-weight: bold; color: #0284c7;")

        self.chk_iqa_table = QCheckBox("Histórico Completo de Medições IQA (53 Parâmetros)")
        self.chk_interf_table = QCheckBox("Tabela Detalhada de Interferências e Vazões (Q90/Qmédia)")
        self.chk_bacias = QCheckBox("Bacias Hidrográficas Cadastradas (12 bacias)")
        self.chk_corpos = QCheckBox("Corpos Hídricos Cadastrados (59 cursos d'água)")

        v_l.addWidget(self.chk_pontos)
        v_l.addWidget(self.chk_outorgas)
        v_l.addWidget(self.chk_iqa_table)
        v_l.addWidget(self.chk_interf_table)
        v_l.addWidget(self.chk_bacias)
        v_l.addWidget(self.chk_corpos)
        h_top.addWidget(grp_layers)

        grp_enrich = QGroupBox("Enriquecimento Analítico Automático")
        v_e = QVBoxLayout(grp_enrich)
        self.chk_enrich_iqa = QCheckBox("Vincular última medição de IQA aos Pontos (colorir por qualidade)")
        self.chk_enrich_iqa.setChecked(True)

        self.chk_enrich_outorga = QCheckBox("Vincular dados de vazão (Q90, Qmédia, Vazão Requerida) às Outorgas")
        self.chk_enrich_outorga.setChecked(True)

        self.chk_auto_style = QCheckBox("Aplicar Estilização Temática Automática")
        self.chk_auto_style.setChecked(True)

        self.chk_create_group = QCheckBox("Agrupar em 'QUALI+ • Dimensão Água (AGERH)'")
        self.chk_create_group.setChecked(True)

        self.chk_zoom = QCheckBox("Ajustar Zoom do mapa à extensão dos dados")
        self.chk_zoom.setChecked(True)

        v_e.addWidget(self.chk_enrich_iqa)
        v_e.addWidget(self.chk_enrich_outorga)
        v_e.addWidget(self.chk_auto_style)
        v_e.addWidget(self.chk_create_group)
        v_e.addWidget(self.chk_zoom)
        h_top.addWidget(grp_enrich)

        layout.addLayout(h_top)

        # Filtros
        grp_filtros = QGroupBox("Filtros Espaciais e Temáticos (Opcional)")
        h_f = QHBoxLayout(grp_filtros)

        h_f.addWidget(QLabel("Município:"))
        self.cmb_municipio = QComboBox()
        self.cmb_municipio.addItems(MUNICIPIOS_ES)
        h_f.addWidget(self.cmb_municipio)

        h_f.addWidget(QLabel("Bacia:"))
        self.cmb_bacia = QComboBox()
        self.cmb_bacia.addItems(BACIAS_ES)
        h_f.addWidget(self.cmb_bacia)

        h_f.addWidget(QLabel("Status Outorga:"))
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Todos", "Concluído", "Aguardando análise", "Em análise", "Certificado de Regularidade"])
        h_f.addWidget(self.cmb_status)

        layout.addWidget(grp_filtros)

        # Destino
        grp_out = QGroupBox("Destino dos Dados")
        h_o = QHBoxLayout(grp_out)

        self.rad_memory = QRadioButton("Carregar como Camadas em Memória (Rápido / Temporário)")
        self.rad_memory.setChecked(True)
        self.rad_gpkg = QRadioButton("Gravar em Arquivo GeoPackage (.gpkg)")
        self.btn_grp_out = QButtonGroup()
        self.btn_grp_out.addButton(self.rad_memory)
        self.btn_grp_out.addButton(self.rad_gpkg)
        self.rad_gpkg.toggled.connect(self.on_gpkg_toggled)

        h_o.addWidget(self.rad_memory)
        h_o.addWidget(self.rad_gpkg)

        self.txt_gpkg_path = QLineEdit()
        self.txt_gpkg_path.setPlaceholderText("Caminho do arquivo .gpkg...")
        self.txt_gpkg_path.setEnabled(False)
        self.btn_browse_gpkg = QPushButton("Procurar...")
        self.btn_browse_gpkg.setEnabled(False)
        self.btn_browse_gpkg.clicked.connect(self.browse_gpkg)

        h_o.addWidget(self.txt_gpkg_path)
        h_o.addWidget(self.btn_browse_gpkg)

        layout.addWidget(grp_out)

        # Barra de Progresso e Botão de Carga
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("Selecione os dados desejados e execute a ingestão via AgerhProvider.")
        self.lbl_status.setStyleSheet("color: #475569; font-size: 8.5pt;")
        layout.addWidget(self.lbl_status)

        h_run = QHBoxLayout()
        self.btn_execute = QPushButton("  Executar Ingestão no QGIS (AgerhProvider)")
        self.btn_execute.setStyleSheet("""
            QPushButton {
                background-color: #0284c7; color: white; font-weight: bold; font-size: 10pt;
                padding: 10px 24px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #0369a1; }
            QPushButton:disabled { background-color: #cbd5e1; }
        """)
        self.btn_execute.clicked.connect(self.on_execute_clicked)
        h_run.addStretch()
        h_run.addWidget(self.btn_execute)
        layout.addLayout(h_run)

    def on_gpkg_toggled(self, checked):
        self.txt_gpkg_path.setEnabled(checked)
        self.btn_browse_gpkg.setEnabled(checked)
        if checked and not self.txt_gpkg_path.text().strip():
            self.txt_gpkg_path.setText(os.path.join(os.path.expanduser("~"), "quali_agua_agerh.gpkg"))

    def browse_gpkg(self):
        fpath, _ = QFileDialog.getSaveFileName(
            self, "Salvar Dados QUALI+ em GeoPackage",
            self.txt_gpkg_path.text().strip() or os.path.join(os.path.expanduser("~"), "quali_agua_agerh.gpkg"),
            "GeoPackage (*.gpkg)"
        )
        if fpath:
            if not fpath.lower().endswith(".gpkg"):
                fpath += ".gpkg"
            self.txt_gpkg_path.setText(fpath)

    def on_execute_clicked(self):
        params = {
            "load_pontos": self.chk_pontos.isChecked(),
            "load_outorgas": self.chk_outorgas.isChecked(),
            "load_iqa_table": self.chk_iqa_table.isChecked(),
            "load_interf_table": self.chk_interf_table.isChecked(),
            "load_bacias": self.chk_bacias.isChecked(),
            "load_corpos": self.chk_corpos.isChecked(),
            "enrich_iqa": self.chk_enrich_iqa.isChecked(),
            "enrich_outorga": self.chk_enrich_outorga.isChecked(),
            "filter_municipio": self.cmb_municipio.currentText(),
            "filter_bacia": self.cmb_bacia.currentText(),
            "filter_status": self.cmb_status.currentText(),
            "auto_style": self.chk_auto_style.isChecked(),
            "output_mode": "gpkg" if self.rad_gpkg.isChecked() else "memory",
            "gpkg_path": self.txt_gpkg_path.text().strip()
        }

        if not any([params["load_pontos"], params["load_outorgas"], params["load_iqa_table"],
                    params["load_interf_table"], params["load_bacias"], params["load_corpos"]]):
            QMessageBox.warning(self, "Aviso", "Selecione ao menos uma camada ou tabela para ingestão.")
            return

        if params["output_mode"] == "gpkg" and not params["gpkg_path"]:
            QMessageBox.warning(self, "Aviso", "Por favor, indique o caminho do arquivo GeoPackage.")
            return

        self.btn_execute.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.lbl_status.setText("Iniciando ingestão federada via AgerhProvider...")

        self.worker = AgerhWorker(params)
        self.worker.progress_changed.connect(self.on_worker_progress)
        self.worker.finished_success.connect(self.on_worker_success)
        self.worker.finished_error.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_progress(self, val, msg):
        self.progress_bar.setValue(val)
        self.lbl_status.setText(msg)

    def on_worker_success(self, layers_dict):
        self.btn_execute.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.lbl_status.setText(f"Sucesso! {len(layers_dict)} camada(s) incorporada(s) à dimensão ÁGUA.")

        proj = QgsProject.instance()
        group = None
        if self.chk_create_group.isChecked():
            root = proj.layerTreeRoot()
            group_name = "QUALI+ • Dimensão ÁGUA (AGERH)"
            group = root.findGroup(group_name)
            if not group:
                group = root.addGroup(group_name)

        combined_extent = QgsRectangle()
        first_extent = True

        is_gpkg = self.rad_gpkg.isChecked()
        gpkg_path = self.txt_gpkg_path.text().strip()

        for layer_name, layer in layers_dict.items():
            if not layer or not layer.isValid():
                continue

            final_layer = layer
            if is_gpkg:
                safe_name = layer_name.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("ç", "c").replace("ã", "a").replace("í", "i").replace("á", "a")
                gpkg_uri = f"{gpkg_path}|layername={safe_name}"
                final_layer = QgsVectorLayer(gpkg_uri, layer_name, "ogr")
                if self.chk_auto_style.isChecked():
                    if "Pontos de Coleta" in layer_name:
                        agerh_svc.apply_iqa_style(final_layer)
                    elif "Outorgas" in layer_name:
                        agerh_svc.apply_outorgas_style(final_layer)

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

        if self.chk_zoom.isChecked() and self.iface and not combined_extent.isEmpty():
            try:
                canvas = self.iface.mapCanvas()
                canvas.setExtent(combined_extent)
                canvas.refresh()
            except Exception:
                pass

        total_features = sum(l.featureCount() for l in layers_dict.values() if l and l.isValid())
        msg = f"QUALI+ (Dimensão Água)\n\nForam incorporadas com sucesso {len(layers_dict)} camada(s) " \
              f"totalizando {total_features:,} registros com metadados de proveniência auditáveis!"
        if is_gpkg:
            msg += f"\n\nGeoPackage gerado em:\n{gpkg_path}"
        QMessageBox.information(self, "QUALI+ • Ingestão Concluída", msg)

    def on_worker_error(self, err_msg):
        self.btn_execute.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.lbl_status.setText("Erro durante a ingestão.")
        QMessageBox.critical(self, "Erro no Provedor AGERH", f"Ocorreu um erro:\n\n{err_msg}")

    # =========================================================================
    # ABA 3: FONTES PLANEJADAS (ROADMAP)
    # =========================================================================
    def setup_tab_roadmap(self):
        layout = QVBoxLayout(self.tab_roadmap)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        lbl_desc = QLabel(
            "<b>Arquitetura Multiprovedor QUALI+ • Fontes Planejadas</b><br>"
            "As fontes abaixo estão catalogadas e modeladas no White Paper do QUALI+. "
            "Elas coexistirão com o conector AGERH na dimensão ÁGUA sem necessidade de refatoração estrutural."
        )
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        txt_roadmap = QTextEdit()
        txt_roadmap.setReadOnly(True)
        txt_roadmap.setStyleSheet("background-color: #f8fafc; font-family: Segoe UI, sans-serif; font-size: 9pt;")

        planned_text = """
===================================================================================
CATÁLOGO DE CONECTORES PREVISTOS (DIMENSÃO TEMÁTICA ÁGUA)
===================================================================================

1. ANA / SNIRH (Agência Nacional de Águas e Saneamento Básico)
   • Escopo: Nacional
   • Produtos: Níveis Fluviométricos, Vazões, Precipitação, Outorgas Federais, SAR Reservatórios
   • Protocolos Planejados: API REST HidroWeb v2, WFS SNIRH
   • Status: PLANEJADO

2. SGB / CPRM - SACE (Serviço Geológico do Brasil)
   • Escopo: Nacional / Regional (Bacia do Rio Doce e Rio Itabapoana)
   • Produtos: Cotas de Alerta e Inundação, Previsão Hidrológica de Cheias
   • Protocolos Planejados: API REST SACE
   • Status: PLANEJADO

3. Cemaden (Centro Nacional de Monitoramento e Alertas de Desastres Naturais)
   • Escopo: Nacional (PCDs nos 78 municípios do ES)
   • Produtos: Precipitação Pluviométrica de Superfície, Níveis em Córregos Urbanos
   • Protocolos Planejados: API REST Cemaden PCDs
   • Status: PLANEJADO

4. Monitor de Secas (ANA / AGERH / SEAMA)
   • Escopo: Nacional / Estadual
   • Produtos: Severidade de Seca (S0 Fraca a S4 Excepcional), Impactos Hídricos
   • Protocolos Planejados: WFS / GeoJSON
   • Status: PLANEJADO

5. AlertaES / Defesa Civil Estadual (CBMES / CEPDEC)
   • Escopo: Estadual
   • Produtos: Avisos de Risco Hidrológico, Alagamentos e Enxurradas
   • Protocolos Planejados: API AlertaES
   • Status: PLANEJADO

6. GloFAS (Copernicus / ECMWF)
   • Escopo: Global
   • Produtos: Previsões de Vazão Ensemble de 1 a 30 dias, Limiares de Extremos
   • Protocolos Planejados: Copernicus Climate Data Store (CDS) API
   • Status: PLANEJADO

7. NASA / JAXA - GPM IMERG
   • Escopo: Global
   • Produtos: Precipitação Calibrada Multissatélite (0.1° / 30 minutos)
   • Protocolos Planejados: NASA Earthdata Cloud / COG
   • Status: PLANEJADO

8. MapBiomas Água
   • Escopo: Nacional
   • Produtos: Série Histórica da Superfície de Água (1985-2024), Corpos Hídricos e Reservatórios
   • Protocolos Planejados: Google Earth Engine Asset / GeoTIFF
   • Status: PLANEJADO

9. Copernicus Sentinel-1 SAR (ESA)
   • Escopo: Global
   • Produtos: Detecção de Lâmina de Água sob Nuvens, Manchas de Inundação Recorrentes
   • Protocolos Planejados: Copernicus Data Space STAC API
   • Status: PLANEJADO

Nota Científica:
Nenhum dado fictício ou simulado é injetado pelo QUALI+. Conectores planejados permanecem
estritamente inativos até a homologação operacional de seus respectivos adaptadores.
"""
        txt_roadmap.setPlainText(planned_text.strip())
        layout.addWidget(txt_roadmap)

    # =========================================================================
    # ABA 4: PROVENIÊNCIA & AUDITORIA
    # =========================================================================
    def setup_tab_provenance(self):
        layout = QVBoxLayout(self.tab_provenance)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        lbl_desc = QLabel(
            "<h3>Rastreabilidade e Linhagem de Dados (DataProvenance)</h3>"
            "<p>Cada camada gerada no QUALI+ recebe automaticamente uma assinatura de proveniência "
            "armazenada em seus metadados internos e propriedades personalizadas do QGIS.</p>"
            "<p><b>Campos padronizados de proveniência:</b></p>"
            "<ul>"
            "<li><b>dimension:</b> Dimensão temática (ex: <code>agua</code>).</li>"
            "<li><b>provider:</b> Identificador do conector (ex: <code>agerh</code>, <code>ana_snirh</code>, <code>glofas</code>).</li>"
            "<li><b>organization:</b> Entidade responsável pela custódia do dado (ex: <code>AGERH</code>, <code>ANA</code>, <code>NASA</code>).</li>"
            "<li><b>dataset:</b> Conjunto de dados específico (ex: <code>pontos_coleta</code>, <code>outorgas</code>).</li>"
            "<li><b>product:</b> Produto analítico associado (ex: <code>qualidade_agua</code>, <code>vazoes</code>).</li>"
            "<li><b>version:</b> Versão do esquema de dados.</li>"
            "<li><b>retrieved_at:</b> Timestamp ISO UTC do momento exato da coleta.</li>"
            "<li><b>observation_time:</b> Período temporal de observação do fenômeno.</li>"
            "<li><b>processing_time:</b> Duração e carimbo de execução do processamento.</li>"
            "<li><b>territory:</b> Recorte territorial de aplicação (ex: <code>Espírito Santo</code>).</li>"
            "<li><b>algorithm:</b> Método de ingestão, reprojeção e junção utilizado.</li>"
            "</ul>"
            "<p>Essa estrutura assegura reprodutibilidade científica, auditoria pública e conformidade com diretrizes "
            "de governança de dados espaciais da SEAMA e órgãos reguladores.</p>"
        )
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)
        layout.addStretch()
