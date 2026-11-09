"""Gera bases ILUSTRATIVAS (sementes fixas) e imagens. Substitua pelas bases reais do IBGE/Atlas via upload no app."""
import numpy as np, pandas as pd
from PIL import Image, ImageDraw
rng = np.random.default_rng(42)
UF = {"AC":("Norte",.663),"AL":("Nordeste",.631),"AP":("Norte",.708),"AM":("Norte",.674),"BA":("Nordeste",.660),
"CE":("Nordeste",.682),"DF":("Centro-Oeste",.824),"ES":("Sudeste",.740),"GO":("Centro-Oeste",.735),"MA":("Nordeste",.639),
"MT":("Centro-Oeste",.725),"MS":("Centro-Oeste",.729),"MG":("Sudeste",.731),"PA":("Norte",.646),"PB":("Nordeste",.658),
"PR":("Sul",.749),"PE":("Nordeste",.673),"PI":("Nordeste",.646),"RJ":("Sudeste",.761),"RN":("Nordeste",.684),
"RS":("Sul",.746),"RR":("Norte",.707),"RO":("Norte",.690),"SC":("Sul",.774),"SP":("Sudeste",.783),
"SE":("Nordeste",.665),"TO":("Norte",.699)}
RACAS = ["Branca","Preta","Parda","Amarela","Indígena"]; FAIXAS = ["0-14","15-29","30-59","60+"]
cl = lambda x, a=0, b=1: np.clip(x, a, b)
idh, mun, pop, alf, ind, mul = [], [], [], [], [], []
for u, (reg, t) in UF.items():
    for ano, sh in {2000: -.09, 2010: 0, 2021: .045}.items():
        t2 = t + sh
        L, E, R = cl(t2+.10+rng.normal(0,.012)), cl(t2-.08+rng.normal(0,.02)), cl(t2+rng.normal(0,.015))
        idh.append([u, reg, ano, round((L*E*R)**(1/3),3), round(L,3), round(E,3), round(R,3),
                    round(max(300, 900+9000*(t-.6)*(1+(ano-2000)/40)+rng.normal(0,250)),0)])
    base = 1200 + 9000*(t-.62); n = 20
    rend = base*rng.lognormal(0, .35, n); rend[rng.integers(n)] *= 3
    for i in range(n):
        mun.append([u, f"Município fictício {u}-{i+1:02d}", round(float(cl(rng.normal(t,.04))),3), round(rend[i],2)])
    tot = 1e6*rng.lognormal(1, .8); pr = rng.dirichlet([4,1,6,.3,.4])
    for ano in (2010, 2022):
        pf = np.array([.26,.27,.37,.10]) + (0 if ano == 2010 else np.array([-.04,-.03,0,.07]))
        for fa, pfa in zip(FAIXAS, pf):
            for sx, ps in (("Mulheres",.515),("Homens",.485)):
                for rc, prc in zip(RACAS, pr):
                    pop.append([u, ano, fa, sx, rc, int(tot*pfa*ps*prc)])
        for sx in ("Mulheres","Homens"):
            for rc, d in zip(RACAS, (2,-1.5,-1.5,2,-8)):
                alf.append([u, ano, sx, rc, round(float(cl(70+150*(t-.6)+d+(.8 if sx=="Mulheres" else 0)+(1.5 if ano==2022 else 0)+rng.normal(0,1),50,99.5)),1)])
        pt = int(tot); pm = int(pt*rng.normal(.515,.004))
        mul.append([u, ano, pt, pm, round(float(rng.normal(46,3)),1), round(base*rng.normal(.82,.05),0), round(base*rng.normal(1.1,.05),0)])
    ip = 3e4*rng.lognormal(0, 1.4) * (8 if u in ("AM","MT","RR","BA") else 1); rur = rng.uniform(.2,.7)
    ind += [[u, "Urbana", int(ip*(1-rur))], [u, "Rural", int(ip*rur)]]
def save(nome, rows, cols): pd.DataFrame(rows, columns=cols).to_csv(f"dados/{nome}.csv", index=False)
save("idhm_uf", idh, ["uf","regiao","ano","idhm","idhm_long","idhm_educ","idhm_renda","investimento_pc"])
save("municipios", mun, ["uf","municipio","idhm","renda_resp"])
save("populacao", pop, ["uf","ano","faixa","sexo","raca","populacao"])
save("alfabetizacao", alf, ["uf","ano","sexo","raca","taxa"])
save("indigenas", ind, ["uf","situacao","populacao"])
save("mulheres", mul, ["uf","ano","pop_total","pop_mulheres","pct_resp_mulheres","rend_mulheres","rend_homens"])
for nome, tit, txt, cor in [("longevidade","LONGEVIDADE","Expectativa de vida ao nascer\n(vida longa e saudável)",(46,125,90)),
        ("educacao","EDUCAÇÃO","Escolaridade e fluxo escolar\n(acesso ao conhecimento)",(52,101,164)),
        ("renda","RENDA","Renda per capita\n(padrão de vida decente)",(196,126,32))]:
    im = Image.new("RGB", (640, 360), cor); d = ImageDraw.Draw(im)
    d.rectangle([20,20,620,340], outline="white", width=4)
    d.text((50,60), f"IDHM — {tit}", fill="white", font_size=36); d.text((50,150), txt, fill="white", font_size=24)
    d.text((50,290), "IDHM = (L × E × R)^(1/3)", fill="white", font_size=22); im.save(f"assets/{nome}.png")
print("ok")
