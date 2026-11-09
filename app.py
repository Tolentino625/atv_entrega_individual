import numpy as np, pandas as pd, plotly.express as px, plotly.graph_objects as go, streamlit as st
from pathlib import Path
from urllib.parse import quote
from estatistica import resumo, tabela, leitura

st.set_page_config(page_title="IDH Brasil — Números que Falam", page_icon="📊", layout="wide")
RAIZ = Path(__file__).parent
BASES = {
 "idhm_uf": ("IDHM por UF", ["uf","regiao","ano","idhm","idhm_long","idhm_educ","idhm_renda","investimento_pc"]),
 "municipios": ("IDHM e renda por município", ["uf","municipio","idhm","renda_resp"]),
 "populacao": ("1 · População por idade, sexo e raça", ["uf","ano","faixa","sexo","raca","populacao"]),
 "alfabetizacao": ("2 · Alfabetização por sexo e raça", ["uf","ano","sexo","raca","taxa"]),
 "indigenas": ("3 · Pessoas indígenas", ["uf","situacao","populacao"]),
 "mulheres": ("4 · Mulheres", ["uf","ano","pop_total","pop_mulheres","pct_resp_mulheres","rend_mulheres","rend_homens"])}

def carregar(chave):
    nome, cols = BASES[chave]; up = st.session_state.get("up_" + chave)
    if up is not None:
        try:
            up.seek(0)
            df = pd.read_csv(up) if up.name.lower().endswith(".csv") else pd.read_excel(up)
            df.columns = [c.strip().lower() for c in df.columns]
            falt = [c for c in cols if c not in df.columns]
            if not falt: return df, True
            st.sidebar.error(f"{nome}: faltam colunas {falt}. Usando dados de demonstração.")
        except Exception as e:
            st.sidebar.error(f"{nome}: erro ao ler arquivo ({e}). Usando dados de demonstração.")
    return pd.read_csv(RAIZ / "dados" / f"{chave}.csv"), False

def cards(r, f="{:.3f}"):
    for col, k in zip(st.columns(6), ["Média","Mediana","IQR","Desvio padrão","Amplitude","Outliers"]):
        col.metric(k, int(r[k]) if k == "Outliers" else f.format(r[k]))

def estat(serie, f="{:.3f}", titulo="Estatísticas descritivas"):
    r = resumo(serie); cards(r, f)
    with st.expander(titulo + " (completas)"):
        st.dataframe(pd.Series(r, name="valor").to_frame().style.format("{:.4f}"))
    st.info("📖 **Leitura estatística:** " + leitura(r, f))

# ---------------- Sidebar ----------------
st.sidebar.title("🎛️ Filtros")
comp = st.sidebar.radio("Componente do IDH", ["Geral","Longevidade","Educação","Renda"])
COL = {"Geral":"idhm","Longevidade":"idhm_long","Educação":"idhm_educ","Renda":"idhm_renda"}[comp]
with st.sidebar.expander("📁 Upload de dados (CSV/XLSX)"):
    st.caption("Envie a base do IBGE/Atlas com as colunas exigidas. Sem upload, usa-se a base de demonstração.")
    for k, (n, c) in BASES.items():
        st.file_uploader(n, type=["csv","xlsx"], key="up_" + k, help="Colunas: " + ", ".join(c))
idh, up_idh = carregar("idhm_uf"); mun, up_mun = carregar("municipios")
pop, up_pop = carregar("populacao"); alf, up_alf = carregar("alfabetizacao")
ind, up_ind = carregar("indigenas"); mul, up_mul = carregar("mulheres")
todas = sorted(idh.uf.unique()); anos_all = sorted(idh.ano.unique())
pad = [u for u in ["MA","PA","AC","BA","MG"] if u in todas]
ufs = st.sidebar.multiselect("UFs", todas, default=pad)
anos = st.sidebar.multiselect("Anos (IDHM)", anos_all, default=anos_all)
if not ufs or not anos: st.warning("Selecione ao menos uma UF e um ano na barra lateral."); st.stop()
ano_ref = max(anos)

st.title("📊 Números que Falam — IDH do Brasil")
st.caption("Startup de análise de dados · Consórcio de governadores: MA, PA, AC, BA e MG · Projeto Integrador (Python e Matemática)")
if not all([up_idh, up_mun, up_pop, up_alf, up_ind, up_mul]):
    st.warning("⚠️ Parte das bases é **ILUSTRATIVA (demonstração)** e não representa dados oficiais. "
               "Para a entrega, exporte as bases reais (Atlas Brasil / SIDRA-IBGE) e envie pelo upload na barra lateral.")

t0, t1, t2, t3, t4, t5, t6, t7 = st.tabs(["🌎 IDH","1 · População","2 · Alfabetização","3 · Indígenas","4 · Mulheres","5 · Renda","📰 Notícias e imagens","🎤 Roteiro"])

# ---------------- IDH ----------------
with t0:
    cur_all = idh[idh.ano == ano_ref]; cur = cur_all[cur_all.uf.isin(ufs)].copy()
    st.subheader(f"{comp} — dispersão entre as {len(cur_all)} UFs em {ano_ref}")
    estat(cur_all[COL])
    dims = {"idhm_long":"Longevidade","idhm_educ":"Educação","idhm_renda":"Renda"}
    cur["puxa_baixo"] = cur[list(dims)].idxmin(axis=1).map(dims)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Radar dos subíndices** (Q1: o que puxa o IDH para baixo?)")
        fig = go.Figure()
        for _, l in cur.iterrows():
            fig.add_trace(go.Scatterpolar(r=[l.idhm_long, l.idhm_educ, l.idhm_renda, l.idhm_long],
                theta=["Longevidade","Educação","Renda","Longevidade"], name=l.uf, fill="toself", opacity=.5))
        fig.update_layout(polar=dict(radialaxis=dict(range=[.4, 1])), margin=dict(t=20)); st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown("**Subíndices por UF**")
        m = cur.melt("uf", list(dims), "dim", "valor"); m["dim"] = m.dim.map(dims)
        st.plotly_chart(px.bar(m, x="uf", y="valor", color="dim", barmode="group", labels={"valor":"Índice","uf":"UF","dim":"Dimensão"}), width="stretch")
    st.success("**Resposta Q1:** " + " · ".join(f"{r.uf}: **{r.puxa_baixo}** ({r[[k for k,v in dims.items() if v==r.puxa_baixo][0]]:.3f})" for _, r in cur.iterrows()))
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Q2 · Evolução temporal**")
        ev = idh[idh.uf.isin(ufs) & idh.ano.isin(anos)]
        st.plotly_chart(px.line(ev, x="ano", y=COL, color="uf", markers=True, labels={COL:comp}).update_xaxes(type="category"), width="stretch")
    with c4:
        st.markdown("**IDHM × investimento público per capita**")
        st.plotly_chart(px.scatter(cur_all, x="investimento_pc", y=COL, color="regiao", hover_name="uf", text="uf",
            labels={"investimento_pc":"Investimento público per capita (R$)", COL:comp}), width="stretch")
        st.caption(f"Correlação de Pearson (27 UFs): r = {cur_all.investimento_pc.corr(cur_all[COL]):.2f}. Correlação não prova causalidade.")
    st.markdown("**Q3 · Municípios e dispersão entre estados**")
    mm = mun[mun.uf.isin(ufs)]
    st.plotly_chart(px.box(mm, x="uf", y="idhm", points="all", hover_name="municipio", labels={"idhm":"IDHM municipal","uf":"UF"}), width="stretch")
    a, b = st.columns(2)
    a.write("🔻 Menores IDHM"); a.dataframe(mm.nsmallest(5, "idhm")[["uf","municipio","idhm"]], hide_index=True)
    b.write("🔺 Maiores IDHM"); b.dataframe(mm.nlargest(5, "idhm")[["uf","municipio","idhm"]], hide_index=True)
    st.dataframe(tabela(mm, "idhm", "uf")[["Média","Mediana","Q1","Q3","IQR","Amplitude","Desvio padrão","Outliers"]].astype(float).round(3))

# ---------------- 1 População ----------------
with t1:
    st.subheader("População por grupo de idade, sexo e raça")
    ap = st.selectbox("Ano", sorted(pop.ano.unique()), index=len(pop.ano.unique()) - 1, key="ap")
    racas = st.multiselect("Raça/cor", sorted(pop.raca.unique()), default=sorted(pop.raca.unique()))
    p = pop[(pop.ano == ap) & pop.raca.isin(racas)]
    pu = p[p.uf.isin(ufs)]
    g = pu.groupby(["faixa","sexo"], as_index=False).populacao.sum(); g.loc[g.sexo == "Homens", "populacao"] *= -1
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(g, y="faixa", x="populacao", color="sexo", orientation="h", title="Pirâmide etária (UFs selecionadas)"), width="stretch")
    c2.plotly_chart(px.bar(pu.groupby(["uf","raca"], as_index=False).populacao.sum(), x="uf", y="populacao", color="raca", title="Composição por raça/cor (%)").update_layout(barnorm="percent"), width="stretch")
    tot = p.groupby("uf").populacao.sum(); idoso = p[p.faixa == "60+"].groupby("uf").populacao.sum() / tot * 100
    d = idoso.rename("pct_60").reset_index().merge(idh[idh.ano == ano_ref][["uf","regiao","idhm_long"]], on="uf")
    st.markdown("**% da população com 60+ anos por UF** (ligação com a dimensão Longevidade)")
    estat(d.pct_60, "{:.2f}")
    st.plotly_chart(px.box(d, x="regiao", y="pct_60", points="all", hover_name="uf", labels={"pct_60":"% 60+"}), width="stretch")

# ---------------- 2 Alfabetização ----------------
with t2:
    st.subheader("Alfabetização por sexo e raça (dimensão Educação)")
    aa = st.selectbox("Ano", sorted(alf.ano.unique()), index=len(alf.ano.unique()) - 1, key="aa")
    sx = st.multiselect("Sexo", sorted(alf.sexo.unique()), default=sorted(alf.sexo.unique()))
    a = alf[(alf.ano == aa) & alf.sexo.isin(sx)]
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(a[a.uf.isin(ufs)].groupby(["raca","sexo"], as_index=False).taxa.mean(), x="raca", y="taxa", color="sexo", barmode="group", labels={"taxa":"Taxa (%)"}, title="Taxa média nas UFs selecionadas"), width="stretch")
    c2.plotly_chart(px.box(a, x="raca", y="taxa", points="all", hover_name="uf", labels={"taxa":"Taxa (%)"}, title="Dispersão entre as UFs"), width="stretch")
    st.markdown("**Estatísticas da taxa de alfabetização (todas as UFs, grupos filtrados)**"); estat(a.taxa, "{:.2f}")
    mu = a.groupby("uf", as_index=False).taxa.mean().merge(idh[idh.ano == ano_ref][["uf","idhm_educ"]], on="uf")
    st.plotly_chart(px.scatter(mu, x="taxa", y="idhm_educ", text="uf", labels={"taxa":"Alfabetização média (%)","idhm_educ":"IDHM Educação"}), width="stretch")
    st.caption(f"Correlação alfabetização × IDHM-Educação: r = {mu.taxa.corr(mu.idhm_educ):.2f}")

# ---------------- 3 Indígenas ----------------
with t3:
    st.subheader("Pessoas indígenas por localização e situação do domicílio")
    i = ind.copy(); piv = i.pivot_table(index="uf", columns="situacao", values="populacao", aggfunc="sum").fillna(0)
    piv["total"] = piv.sum(axis=1); piv["pct_rural"] = piv.get("Rural", 0) / piv.total * 100; piv = piv.reset_index()
    st.plotly_chart(px.bar(i[i.uf.isin(ufs)], x="uf", y="populacao", color="situacao", barmode="group", title="Urbano × rural nas UFs selecionadas"), width="stretch")
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(piv.nlargest(10, "total"), x="uf", y="total", title="10 UFs com mais pessoas indígenas"), width="stretch")
    c2.plotly_chart(px.box(piv, y="pct_rural", points="all", hover_name="uf", labels={"pct_rural":"% rural"}, title="Dispersão do % rural entre UFs"), width="stretch")
    st.markdown("**População indígena por UF (distribuição muito assimétrica)**"); estat(piv.total, "{:,.0f}")
    st.markdown("**% rural por UF**"); estat(piv.pct_rural, "{:.1f}")

# ---------------- 4 Mulheres ----------------
with t4:
    st.subheader("Mulheres: presença, chefia domiciliar e paridade de renda")
    am = st.selectbox("Ano", sorted(mul.ano.unique()), index=len(mul.ano.unique()) - 1, key="am")
    m = mul[mul.ano == am].copy(); m["pct_mulheres"] = m.pop_mulheres / m.pop_total * 100; m["paridade"] = m.rend_mulheres / m.rend_homens * 100
    ms = m[m.uf.isin(ufs)]
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(ms, x="uf", y="pct_mulheres", labels={"pct_mulheres":"% de mulheres"}, title="% de mulheres na população"), width="stretch")
    c2.plotly_chart(px.bar(ms, x="uf", y="paridade", labels={"paridade":"Renda mulheres / homens (%)"}, title="Paridade de rendimento dos responsáveis").add_hline(y=100, line_dash="dash"), width="stretch")
    st.plotly_chart(px.box(m.melt("uf", ["pct_resp_mulheres","paridade"], "indicador", "valor"), x="indicador", y="valor", points="all", hover_name="uf"), width="stretch")
    st.markdown("**Paridade de rendimento (todas as UFs)**"); estat(m.paridade, "{:.1f}")
    st.markdown("**% de domicílios com mulher responsável**"); estat(m.pct_resp_mulheres, "{:.1f}")

# ---------------- 5 Renda ----------------
with t5:
    st.subheader("Rendimento dos responsáveis pelo domicílio (dimensão Renda)")
    r = mun[mun.uf.isin(ufs)]
    rr = resumo(r.renda_resp)
    fig = px.histogram(r, x="renda_resp", nbins=25, labels={"renda_resp":"Rendimento (R$)"})
    fig.add_vline(x=rr["Média"], line_color="red", annotation_text="Média"); fig.add_vline(x=rr["Mediana"], line_color="green", annotation_text="Mediana")
    c1, c2 = st.columns(2)
    c1.plotly_chart(fig, width="stretch")
    c2.plotly_chart(px.box(r, x="uf", y="renda_resp", points="all", hover_name="municipio", labels={"renda_resp":"Rendimento (R$)"}), width="stretch")
    estat(r.renda_resp, "{:,.0f}")
    st.dataframe(tabela(r, "renda_resp", "uf")[["Média","Mediana","Q1","Q3","IQR","Desvio padrão","Outliers"]].astype(float).round(1))
    mr = mun.groupby("uf", as_index=False).renda_resp.median().merge(idh[idh.ano == ano_ref][["uf","idhm_renda"]], on="uf")
    st.plotly_chart(px.scatter(mr, x="renda_resp", y="idhm_renda", text="uf", labels={"renda_resp":"Mediana do rendimento (R$)","idhm_renda":"IDHM Renda"}), width="stretch")

# ---------------- Notícias e imagens ----------------
with t6:
    st.subheader("Infográficos — as três dimensões do IDHM")
    for col, n in zip(st.columns(3), ["longevidade","educacao","renda"]):
        col.image(str(RAIZ / "assets" / f"{n}.png"), width="stretch")
    st.subheader("Reportagens e fontes")
    st.caption("Links de busca atualizados automaticamente (nunca quebram). Escolha 2–3 reportagens para citar na apresentação.")
    for t, q in [("Projetos de superação da extrema pobreza no Brasil","superação da extrema pobreza Brasil projetos"),
                 ("IDH e IDHM dos estados brasileiros","IDHM estados Atlas Brasil PNUD"),
                 ("Desigualdade social e regional no Brasil — IBGE","IBGE desigualdade regional síntese de indicadores sociais")]:
        st.markdown(f"- 🔎 [{t}](https://news.google.com/search?q={quote(q)}&hl=pt-BR&gl=BR&ceid=BR:pt-419)")
    st.markdown("**Fontes oficiais:** [Atlas do Desenvolvimento Humano](https://www.atlasbrasil.org.br) · [SIDRA/IBGE](https://sidra.ibge.gov.br) · [Agência IBGE Notícias](https://agenciadenoticias.ibge.gov.br) · [PNUD Brasil](https://www.undp.org/pt/brazil)")

# ---------------- Roteiro ----------------
with t7:
    st.subheader("Roda de conversa — roteiro da startup")
    st.markdown("""
**Cenário:** o consórcio de governadores (João-MA, Helder-PA, Gladson-AC, Susu-BA, Verinha-MG) quer um fundo regional para reduzir desigualdades.

**Divisão (1 estudante por indicador):** 1 População · 2 Alfabetização · 3 Indígenas · 4 Mulheres · 5 Renda. A aba **IDH** é apresentada pelo grupo.

**Roteiro de 2 min por estudante:** (1) qual pergunta dos governadores o seu indicador ajuda a responder; (2) média × mediana e IQR; (3) outliers e o que significam; (4) qual dimensão do IDH ele explica; (5) recomendação de investimento.

**Perguntas de negócio:** dimensão que mais puxa o IDH para baixo · evolução desde 2000 · municípios extremos e dispersão (IQR/desvio padrão).
""")
