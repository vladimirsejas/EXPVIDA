"""Sensibilidade do tau (homens 30-59) ao sub-registro de obitos. Cobertura por UF: Queiroz et al. 2017, Rev Bras Epidemiol 20(S1):21-33, Tabela 1 (homens).
Cenario: obitos corrigidos = obitos / c_UF, com c_UF = min(1, cobertura publicada); k multiplica o deficit publicado (1-c)."""
import sys, numpy as np
sys.dont_write_bytecode=True
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import divergencia_modelo as dm
UF=[11,12,13,14,15,16,17,21,22,23,24,25,26,27,28,29,31,32,33,35,41,42,43,50,51,52,53]
SEG_0010=[.89,.86,.91,.87,.77,.82,.86,.78,.88,.87,.91,.91,.95,.95,.95,.91,.93,1.01,.96,1.00,.99,.94,.99,.98,.92,.90,1.00]
SEG_9100=[.98,1.08,.92,1.02,.84,.85,.70,.79,.85,.87,.91,.96,.96,.97,.94,.91,.94,.96,.97,.97,1.01,.96,.98,.99,.92,.89,1.07]
GGB_0010=[.94,.93,.99,1.01,.79,.92,.99,.97,.98,.97,1.01,.98,1.00,1.00,1.01,1.00,1.00,1.09,1.00,1.01,1.04,1.00,1.02,1.09,1.00,.98,1.00]
D,PY,cod=dm.carregar(); cols=dm.BANDAS["30-59"]
uf_idx=np.array([UF.index(int(c[:2])) for c in cod])
def tau(per,sx,c=None):
    d=D[(per,sx)].copy(); py=PY[(per,sx)]
    if c is not None: d=d/c[:,None]
    o,E=dm.esperados(d,py,cols); return dm.ajustar(o,E)['tau']
def cov(v,k): v=np.minimum(1.0,np.array(v)); return (1-k*(1-v))[uf_idx]
ref=tau("2022-2024",1)
print("tau 2022-2024 (sem correcao): %.3f"%ref)
print("%-34s %s"%("cenario (2000-2004, homens 30-59)","tau corrigido"))
print("%-34s %.3f"%("sem correcao",tau("2000-2004",1)))
for nome,v in (("GGB 2000/2010 (menor deficit)",GGB_0010),("SEG-adj 2000/2010",SEG_0010),("SEG-adj 1991/2000",SEG_9100)):
    for k in (1,2,3):
        print("%-34s %.3f"%("%s x%d deficit"%(nome,k),tau("2000-2004",1,cov(v,k))))
print("\n2005-2009 com SEG-adj 2000/2010:")
for k in (1,2,3): print("x%d deficit: %.3f (sem correcao %.3f)"%(k,tau("2005-2009",1,cov(SEG_0010,k)),tau("2005-2009",1)))
