import sys, math, numpy as np, pandas as pd
from scipy import optimize
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import divergencia_modelo as dm
D,PY,cod=dm.carregar()
r=pd.read_csv(__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/IDHM_RE_POR_MICRORREGIAO.csv',sep=';',dtype={'microrregiao':str})
def X(ano):
    s=r[r.ANO==ano].set_index('microrregiao').loc[cod]
    return s[['IDHM_R','IDHM_E']].to_numpy()
X00,X10=X(2000),X(2010)
def cov(per):
    x={'2000-2004':X00,'2005-2009':(X00+X10)/2}.get(per,X10)
    return (x-x.mean(0))/x.std(0)
def fit(d,E,x):
    ok=E>0; d,E,x=d[ok],E[ok],x[ok]; lE=np.log(E)
    mu0=math.log(d.sum()/E.sum())
    f=lambda t:-dm.loglik(t[0],math.exp(t[3]),d,lE+x@t[1:3])
    best=None
    for lt in (math.log(.1),math.log(.02)):
        o=optimize.minimize(f,[mu0,0,0,lt],method='L-BFGS-B',bounds=[(-2,2),(-2,2),(-2,2),(math.log(dm.TAU_MIN),math.log(dm.TAU_MAX))])
        if best is None or o.fun<best.fun: best=o
    return math.exp(best.x[3]),best.x[1:3]
per_list=[p for p in dm.PERIODOS]
rows=[]
for per in per_list:
    for sx in dm.SEXOS:
        d,py=D[(per,sx)],PY[(per,sx)]; x=cov(per)
        for nome,cols in dm.BANDAS.items():
            obs,E=dm.esperados(d,py,cols)
            a=dm.ajustar(obs,E); t1,b=fit(obs,E,x)
            rows.append(dict(periodo=per,sexo=sx,banda=nome,obitos=int(obs.sum()),tau_sem=a['tau'],tau_com=t1,reducao_pct=100*(1-t1/a['tau']) if a['tau']>0.01 else np.nan,b_renda=b[0],b_educ=b[1]))
o=pd.DataFrame(rows); o.to_csv(__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/TAU_COM_E_SEM_CONDICOES_DE_VIDA.csv',sep=';',index=False)
pd.set_option('display.width',200); print(o.round(3).to_string())
