# QUALI+ • Dimensão Temática ÁGUA (Complemento QGIS)

Plataforma de inteligência territorial e monitoramento ambiental para o **QGIS** (versão 3.22 ou superior), estruturada segundo o **White Paper QUALI+** pelo Governo do Estado do Espírito Santo (**SEAMA / AGERH**).

---

## 🏛️ Princípio Arquitetural Central

> **AGERH NÃO É O MÓDULO ÁGUA. AGERH É UMA DAS FONTES DO MÓDULO ÁGUA.**

A dimensão **ÁGUA** do QUALI+ é uma dimensão temática agregadora de múltiplas fontes estaduais, nacionais e globais. O sistema distingue rigorosamente:

1. **Dimensão Temática**: `Água` (recursos hídricos, qualidade, extremos e segurança hídrica).
2. **Fontes / Conectores (Providers)**: Provedores de dados com seus respectivos protocolos de acesso.
3. **Produtos Analíticos (Products)**: Camadas e séries temáticas consumidas pelos usuários e tomadores de decisão.

```text
ÁGUA (Dimensão Temática)
│
├── FONTES / CONECTORES (Providers)
│   ├── AGERH / HidroAgerh         [🟢 OPERACIONAL / DISPONÍVEL]
│   │   ├── Pontos de Coleta (IQA)
│   │   ├── Dados de Monitoramento IQA
│   │   ├── Outorgas de Direito de Uso
│   │   ├── Interferências e Vazões
│   │   ├── Bacias Hidrográficas
│   │   └── Corpos Hídricos
│   │
│   ├── ANA / SNIRH / Hidroweb     [⏳ PLANEJADO]
│   ├── SGB / CPRM - SACE          [⏳ PLANEJADO]
│   ├── Cemaden - PCDs Hidro       [⏳ PLANEJADO]
│   ├── Monitor de Secas           [⏳ PLANEJADO]
│   ├── AlertaES / Defesa Civil    [⏳ PLANEJADO]
│   ├── GloFAS (Copernicus)        [⏳ PLANEJADO]
│   ├── NASA / GPM IMERG           [⏳ PLANEJADO]
│   ├── MapBiomas Água             [⏳ PLANEJADO]
│   └── Copernicus Sentinel-1 SAR  [⏳ PLANEJADO]
│
└── PRODUTOS ANALÍTICOS (Products)
    ├── Qualidade da Água (IQA)
    ├── Níveis Fluviométricos (Cotas)
    ├── Vazões Fluviais
    ├── Precipitação Pluviométrica
    ├── Outorgas de Uso da Água
    ├── Interferências e Balanço
    ├── Reservatórios e Barramentos
    ├── Inundações e Manchas de Cheia
    ├── Extremos Hidrológicos (Secas / Cheias)
    └── Segurança Hídrica
```

---

## 🧩 Arquitetura de Software

```text
modules/
└── agua/
    ├── base.py                 # Contratos BaseDataProvider, ProviderStatus, BaseProduct
    ├── registry.py             # SourceRegistry e ProductRegistry centrais
    ├── provenance.py           # Gestão de linhagem e metadados DataProvenance
    │
    ├── providers/
    │   ├── base.py             # Contrato de provedor
    │   ├── agerh/              # Conector Operacional AGERH
    │   │   ├── adapter.py      # AgerhProvider (Adapter em torno do AgerhDataLoader)
    │   │   ├── service.py      # Camada de download, parsing e montagem vetorial
    │   │   └── worker.py       # Thread de segundo plano (não bloqueante)
    │   ├── ana/                # AnaProvider (status: planned)
    │   ├── sgb/                # SgbProvider (status: planned)
    │   ├── cemaden/            # CemadenProvider (status: planned)
    │   ├── monitor_secas/      # MonitorSecasProvider (status: planned)
    │   ├── alerta_es/          # AlertaEsProvider (status: planned)
    │   ├── glofas/             # GlofasProvider (status: planned)
    │   ├── nasa_gpm/           # NasaGpmProvider (status: planned)
    │   ├── mapbiomas_agua/     # MapbiomasAguaProvider (status: planned)
    │   └── sentinel1/          # Sentinel1Provider (status: planned)
    │
    ├── products/               # Produtos Analíticos normalizados
    │   ├── qualidade_agua/
    │   ├── hidrologia/
    │   ├── precipitacao/
    │   ├── inundacao/
    │   ├── outorgas/
    │   └── seguranca_hidrica/
    │
    └── ui/
        └── dialog.py           # Interface agregadora QUALI+ Dimensão Água
```

---

## 🔒 Proveniência e Auditoria Científica (`DataProvenance`)

Cada camada espacial ou tabela gerada no QUALI+ recebe automaticamente uma assinatura auditável de linhagem gravada em suas `CustomProperties` e nos metadados do QGIS:

- `dimension`: `agua`
- `provider`: Identificador da fonte (ex: `agerh`)
- `organization`: Entidade de custódia (ex: `AGERH`, `ANA`, `NASA`)
- `dataset`: Conjunto de dados específico (ex: `pontos_coleta`, `outorgas`)
- `product`: Produto analítico associado
- `retrieved_at`: Timestamp UTC exato da coleta
- `territory`: Recorte territorial (`Espírito Santo`)
- `algorithm`: Método de ingestão, conversão geodésica e junção

---

## 🌊 Conector Operacional AGERH (Implementado no MVP)

| Conjunto de Dados | Geometria / Formato | CRS / Referência | Registros | Produto Analítico |
| :--- | :--- | :--- | :--- | :--- |
| **Pontos de Coleta IQA** | Vetor de Pontos | **EPSG:4326** (WGS 84) | 112 estações | `qualidade_agua` |
| **Outorgas** | Vetor de Pontos | **EPSG:31984** (SIRGAS 2000 UTM 24S) | ~10.846 processos | `outorgas` |
| **Histórico IQA** | Tabela (53 parâmetros) | — | ~1.810 coletas | `qualidade_agua` |
| **Interferências** | Tabela (vazões mensais) | — | ~10.014 registros | `interferencias` |
| **Bacias Hidrográficas**| Tabela de Referência | — | 12 bacias | `seguranca_hidrica` |
| **Corpos Hídricos** | Tabela de Referência | — | 59 cursos d'água | `seguranca_hidrica` |

- **Enriquecimento Inteligente**: Vincula automaticamente a última medição de qualidade aos pontos IQA e as vazões ($Q_{90}$, $Q_{\text{média}}$, vazão máxima requerida) às outorgas.
- **Simbologia Automática**: Estilos temáticos por classe de qualidade (IQA) e por tipo de interferência (captação, barramento, efluentes).
- **Filtros Flexíveis**: Filtragem por qualquer um dos 78 municípios capixabas, bacias hidrográficas e status.
- **Modos de Saída**: Camadas em Memória (ágeis) ou exportação em GeoPackage (`.gpkg`).

---

## 📦 Instalação e Atualização

Execute o instalador:
```powershell
python install_plugin.py
```
Ou carregue o arquivo `agerh_hidro.zip` diretamente no menu **Complementos** > **Instalar a partir do ZIP** no QGIS.

Ao iniciar o QGIS, acesse pelo menu superior **QUALI+** > **Dimensão Água** ou clique no botão da barra de ferramentas.

