import os,sys,numpy as np,pandas as pd
sys.dont_write_bytecode=True
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import divergencia_modelo as dm, causas_tau as ct, causas_comparacao as cc
a=pd.read_csv(os.path.join(ct.P,"CAUSAS_OBITOS_2015_2019.csv"),sep=";",dtype={"microrregiao":str}); a.insert(0,"periodo","2015-2019")
b=pd.read_csv(os.path.join(ct.P,"CAUSAS_OBITOS_OUTROS_PERIODOS.csv"),sep=";",dtype={"microrregiao":str})
df=pd.concat([a,b],ignore_index=True)
D,PY,cod=dm.carregar(); cols=dm.BANDAS["30-59"]
for sx in (1,2):
  print('sexo',sx)
  for per in dm.PERIODOS:
    d=df[df.periodo==per]; py=PY[(per,sx)]
    tot=cc.matriz(d,cod,sx,"todas"); md=cc.matriz(d,cod,sx,"mal_definidas")
    ex=tot-md
    r=[]
    for nome,M in (("todas",tot),("sem mal definidas",ex)):
        o,E=dm.esperados(M,py,cols); r.append(dm.ajustar(o,E)['tau'])
    share=md[:,cols].sum()/tot[:,cols].sum()
    o,E=dm.esperados(md,py,cols)
    print(per,'tau todas %.3f | sem mal definidas %.3f | mal definidas %.1f%% dos obitos'%(r[0],r[1],100*share))
