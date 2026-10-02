# AGERH Hidro Dados - Complemento QGIS

Complemento Python para o **QGIS** (3.22 ou superior) desenvolvido para integrar, visualizar e analisar espacialmente os dados públicos de recursos hídricos disponibilizados pela **Agência Estadual de Recursos Hídricos do Espírito Santo (AGERH)**.

---

## 🌊 APIs Integradas da AGERH

O plugin consome diretamente as APIs de dados abertos do portal Hidro AGERH:

| Conjunto de Dados | Endpoint da API | Formato | Tipo de Camada / Geometria | CRS / Referência |
| :--- | :--- | :--- | :--- | :--- |
| **Pontos de Coleta IQA** | `https://hidro.agerh.es.gov.br/exportar_iqa?type=pontos_coleta` | XML | Vetor de Pontos | EPSG:4326 (WGS 84) |
| **Dados IQA (Monitoramento)** | `https://hidro.agerh.es.gov.br/exportar_iqa?type=dados_iqa` | XML | Tabela Não-Espacial (53 campos) | — |
| **Outorgas** | `https://hidro.agerh.es.gov.br/exportar_outorga?type=outorgas` | XML | Vetor de Pontos | EPSG:31984 (SIRGAS 2000 / UTM 24S) |
| **Interferências** | `https://hidro.agerh.es.gov.br/exportar_outorga?type=interferencias` | XML | Tabela Não-Espacial (vazões mensais) | — |
| **Bacias Hidrográficas** | `https://hidro.agerh.es.gov.br/exportar_iqa?type=bacias` | XML | Tabela de Referência | — |
| **Corpos Hídricos** | `https://hidro.agerh.es.gov.br/exportar_iqa?type=corpos_hidricos` | XML | Tabela de Referência | — |

---

## 🚀 Funcionalidades Principais

1. **Camadas Espaciais Automáticas**:
   - **Pontos de Coleta (Qualidade da Água)**: Plota todas as estações de amostragem no Espírito Santo com opção de anexar a **última medição de IQA** (valor numérico, classe, data, pH, oxigênio dissolvido, turbidez, coliformes).
   - **Outorgas de Recursos Hídricos**: Plota os pontos de captação, barramento e lançamento de efluentes em coordenadas UTM Zone 24S (SIRGAS 2000), vinculando dados de vazões requeridas, Q90 e Qmédia.
2. **Simbologia Temática Pronta**:
   - Classificação automática dos pontos IQA por qualidade da água (*Ótima, Boa, Média, Ruim, Péssima*).
   - Classificação automática das outorgas por tipo de interferência (*Captação Superficial, Subterrânea, Barramento, Lançamento de Efluentes, etc.*).
3. **Filtros Espaciais e Administrativos**:
   - Filtragem rápida por qualquer um dos **78 municípios capixabas**.
   - Filtragem por **Bacia Hidrográfica** (Doce, Jucu, Santa Maria da Vitória, Itapemirim, etc.).
   - Filtragem por **Status da Outorga** (*Concluído, Aguardando análise, etc.*) ou **Tipo de Interferência**.
4. **Exportação Flexível**:
   - **Camadas em Memória (Memory Layer)**: Ideal para visualização imediata e temporária no projeto.
   - **GeoPackage (.gpkg)**: Salva todas as camadas e tabelas selecionadas em um arquivo consolidado e de alta performance no disco.
5. **Alta Performance e Sem Congelamento**:
   - Downloads e conversões executados em segundo plano via `QThread`, mantendo a interface do QGIS responsiva.
   - Sistema de cache local inteligente para evitar downloads repetidos de arquivos grandes (como a tabela de interferências com ~35 MB).

---

## 📦 Como Instalar no QGIS

### Método 1: Instalação Automática (Recomendado)
Execute o script `install_plugin.py` com o Python do QGIS ou Python padrão do sistema:

```powershell
python install_plugin.py
```
*(Ele copia automaticamente os arquivos para `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\agerh_hidro`)*

### Método 2: Instalar a partir do arquivo ZIP no QGIS
1. No QGIS, acesse o menu **Complementos** > **Gerenciar e Instalar Complementos...**
2. Clique na aba lateral **Instalar a partir do ZIP**.
3. Selecione o arquivo `agerh_hidro.zip` gerado na pasta do projeto.
4. Clique em **Instalar complemento**.

### Método 3: Cópia Manual
Copie toda a pasta `agerh_hidro_qgis_plugin` para o diretório de complementos do QGIS:
- **Windows**: `C:\Users\<Seu_Usuario>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\agerh_hidro`

---

## 🖥️ Como Utilizar

1. No QGIS, clique no ícone da gota azul na barra de ferramentas ou no menu superior **AGERH** > **AGERH Hidro Dados**.
2. Na aba **1. Camadas & Tabelas**, selecione quais dados deseja carregar.
3. Na aba **2. Filtros**, opcionalmente selecione um município ou bacia específica para recortar os dados.
4. Na aba **3. Destino & Estilo**, escolha entre carregar na memória ou salvar em GeoPackage.
5. Clique no botão **Carregar Dados no QGIS**.

---

## 🛠️ Tecnologias e Dependências
- **QGIS**: Versão 3.22 ou superior
- **PyQt5 / PyQt6**: Interface gráfica nativa do QGIS
- **Python 3**: Bibliotecas padrão (`urllib`, `xml.etree.ElementTree`, `ssl`, `json`)
- **Sem dependências externas adicionais** (tudo roda nativamente dentro do ambiente Python do QGIS).
