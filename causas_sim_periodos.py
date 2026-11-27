"""
Projeto: Quando o territorio importa (C:\\EXPVIDA) - ESTUDO 2, CAUSAS DE MORTE, demais periodos (separado do EXPVIDA principal).
Como usar: abra este arquivo no VS Code e clique em "Run Python File". Nada mais. Leva cerca de 30 a 40 minutos.
Faz o mesmo que causas_sim.py (mesmas funcoes, mesmos grupos de causa), para os anos que faltam:
2000-2014 e 2020-2024 (2015-2019 ja foi feito). Os arquivos baixados ficam numa pasta temporaria do Windows, apagada no fim;
se parar, rode de novo e continua de onde parou.
Grava CAUSAS_OBITOS_OUTROS_PERIODOS.csv (periodo;microrregiao;sexo;idade_inicio;causa;obitos) e CAUSAS_QUALIDADE_OUTROS.csv.
Nao altera nenhum arquivo do EXPVIDA.
"""
import concurrent.futures, csv, os, shutil, sys, tempfile, time
from collections import defaultdict
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brasil_expectativa as be
import causas_sim as cs

PERIODOS = {"2000-2004": range(2000, 2005), "2005-2009": range(2005, 2010), "2010-2014": range(2010, 2015),
            "2020-2021 pandemia": range(2020, 2022), "2022-2024": range(2022, 2025)}
ANO_PER = {a: p for p, r in PERIODOS.items() for a in r}
cs.CACHE = os.path.join(tempfile.gettempdir(), "expvida_causas_cache2_v2")


def principal():
    os.makedirs(cs.CACHE, exist_ok=True)
    cs.carregar_mapa()
    lista = [(uf, a) for a in sorted(ANO_PER) for uf in cs.UFS]
    falhas, feitos, t0 = [], 0, time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cs.PROCESSOS) as ex:
        fut = {ex.submit(cs.tarefa, uf, a): (uf, a) for uf, a in lista}
        for f in concurrent.futures.as_completed(fut):
            feitos += 1
            uf, a = fut[f]
            try:
                r = f.result(); estado = "%s %.0fs" % (r[3], r[2])
            except Exception as e:
                falhas.append((uf, a)); estado = "FALHOU: %s" % e
            print("[%d/%d] %s %d - %s (decorrido %.0f min)" % (feitos, len(lista), uf, a, estado, (time.time() - t0) / 60), flush=True)
    if falhas:
        print("\nFalharam %d arquivos; rode de novo. Nada foi gravado." % len(falhas)); return
    soma, qual = defaultdict(int), []
    for uf, a in lista:
        r = be._ler_pickle(os.path.join(cs.CACHE, "causas_%s_%d.pkl" % (uf, a)))
        for (mic, sx, g, gc), n in r["cont"].items():
            soma[(ANO_PER[a], mic, sx, g, gc)] += n
        qual.append([uf, a] + [r["q"][c] for c in ("total", "sexo_ign", "idade_ign", "municipio_ign", "sem_causa")])
    with open(os.path.join(cs.PASTA, "CAUSAS_OBITOS_OUTROS_PERIODOS.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["periodo", "microrregiao", "sexo", "idade_inicio", "causa", "obitos"])
        for (p, mic, sx, g, gc), n in sorted(soma.items()):
            w.writerow([p, mic, sx, cs.inv_idade(g), gc, n])
    with open(os.path.join(cs.PASTA, "CAUSAS_QUALIDADE_OUTROS.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["uf", "ano", "obitos_lidos", "sexo_ignorado", "idade_ignorada", "municipio_ignorado", "sem_causa"]); w.writerows(qual)
    shutil.rmtree(cs.CACHE, ignore_errors=True)
    print("\nPronto. Gravados CAUSAS_OBITOS_OUTROS_PERIODOS.csv e CAUSAS_QUALIDADE_OUTROS.csv. Pode fechar.")


if __name__ == "__main__":
    principal()
