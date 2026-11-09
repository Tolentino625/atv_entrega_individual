"""Funções de estatística descritiva (validadas com a Matemática)."""
import numpy as np, pandas as pd

def resumo(s):
    s = pd.Series(s).dropna().astype(float)
    q1, q2, q3 = s.quantile([.25, .5, .75]); iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    moda = s.round(3).mode()
    return {"N": len(s), "Média": s.mean(), "Mediana": q2,
            "Moda": moda.iloc[0] if len(moda) else np.nan,
            "Q1": q1, "Q3": q3, "IQR": iqr, "Amplitude": s.max() - s.min(),
            "Variância": s.var(), "Desvio padrão": s.std(),
            "Mínimo": s.min(), "Máximo": s.max(),
            "Limite inf.": lo, "Limite sup.": hi,
            "Outliers": int(((s < lo) | (s > hi)).sum())}

def tabela(df, col, por):
    return pd.DataFrame({k: resumo(g[col]) for k, g in df.groupby(por)}).T

def leitura(r, f="{:.3f}"):
    m, md = r["Média"], r["Mediana"]
    if m > md * 1.02: forma = "assimetria à direita (valores altos puxam a média para cima)"
    elif m < md * 0.98: forma = "assimetria à esquerda (valores baixos puxam a média para baixo)"
    else: forma = "distribuição aproximadamente simétrica (média ≈ mediana)"
    return (f"Média {f.format(m)} × mediana {f.format(md)}: {forma}. "
            f"A metade central dos dados varia {f.format(r['IQR'])} (IQR) e o desvio padrão é {f.format(r['Desvio padrão'])}. "
            f"Pela regra 1,5·IQR há {r['Outliers']} outlier(s); quando existem, a mediana é a medida mais confiável.")
