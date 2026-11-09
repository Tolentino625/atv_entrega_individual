# Números que Falam — IDH do Brasil (Streamlit)
Projeto Integrador (Python e Matemática). Tema: **IDH/IDHM** (persona 4: consórcio de governadores MA, PA, AC, BA e MG).
A aba **IDH** é do grupo; as abas **1 a 5** são as partes individuais (um estudante por indicador).

## Executar
    pip install -r requirements.txt
    streamlit run app.py

## ⚠️ Dados
`dados/` contém bases **ILUSTRATIVAS**, geradas por `gerar_dados_demo.py` (sementes fixas). **Não são dados oficiais.**
Para a entrega, baixe as bases reais (Atlas Brasil para IDHM; SIDRA/IBGE para os demais), ajuste os nomes das colunas ao modelo dos CSVs de `dados/` e envie pelo upload da barra lateral (ou substitua os arquivos).

## Estrutura
- `app.py` — dashboard (filtros, cards, gráficos, notícias, roteiro) · `estatistica.py` — média, mediana, moda, quartis, IQR, amplitude, variância, desvio padrão e outliers (1,5·IQR)
- `dados/` — bases e modelos de colunas · `assets/` — infográficos

## Alinhamento à rubrica
Upload + filtros (0,75) · estatísticas e Q1–Q3 (0,90) · barras, boxplot, radar, dispersão, notícias e imagens (0,60) · roteiro da roda de conversa (0,75).
