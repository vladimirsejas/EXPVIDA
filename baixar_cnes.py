"""
Projeto: EXPVIDA (C:\\EXPVIDA) - equipes de saude da familia/atencao basica por municipio (CNES, arquivos EP).

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva uns 10 minutos.
Grava CNES_EQUIPES_MUNICIPIO.csv (ano;municipio;tipo_eqp;equipes) e CNES_LOG.txt (com diagnostico).
"""
import csv
import os
import time

import baixar_socioeconomicos as bs

PASTA = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ CNES equipes (versao com diagnostico)
DIAG = {}


def contar_ep(uf, ano):
    from collections import defaultdict
    bruto = bs.be._baixar(bs.CAMINHO_EP % (uf, ano % 100))
    dbf = bs.inv.dbc_para_dbf(bruto)
    n_reg, tam_cab, tam_reg, cols = bs.inv.ler_dbf(dbf)
    pos = {nome: (a, b) for nome, a, b in cols}
    m01 = pos.get("CODUFMUN") or pos.get("CO_MUNICIPIO_GESTOR")
    t01 = pos.get("TIPO_EQP") or pos.get("TP_EQUIPE")
    d01 = pos.get("DT_DESAT")
    if not m01 or not t01:
        raise RuntimeError("colunas: %s" % ",".join(pos))
    cont = defaultdict(int)
    vistos, desat, exemplos = 0, 0, []
    base = tam_cab
    for _ in range(n_reg):
        if base + tam_reg > len(dbf):
            break
        if dbf[base] != 0x2A:
            vistos += 1
            ativa = True
            if len(exemplos) < 2:
                exemplos.append({n: dbf[base + a:base + b].strip().decode("latin-1") for n, a, b in cols})
            if d01:
                dt = dbf[base + d01[0]:base + d01[1]].strip().strip(b"0")
                ativa = dt == b""
            mun = dbf[base + m01[0]:base + m01[1]].strip()[:6].decode("latin-1")
            tp = dbf[base + t01[0]:base + t01[1]].strip().decode("latin-1")
            cont[(mun, tp, "ativa" if ativa else "com_data_desativacao")] += 1
            if not ativa:
                desat += 1
        base += tam_reg
    DIAG[(uf, ano)] = (n_reg, vistos, desat, exemplos, list(pos))
    return dict(cont)


def parte_cnes(saida):
    import concurrent.futures
    from collections import defaultdict
    tot = defaultdict(int)
    tarefas = [(uf, a) for a in bs.CNES_ANOS for uf in bs.be.UFS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        fut = {ex.submit(contar_ep, uf, a): (uf, a) for uf, a in tarefas}
        for i, f in enumerate(concurrent.futures.as_completed(fut), 1):
            uf, a = fut[f]
            try:
                for (mun, tp, st), n in f.result().items():
                    tot[(a, mun, tp, st)] += n
                print("[%d/%d] CNES %s %d ok" % (i, len(tarefas), uf, a), flush=True)
            except Exception as e:
                bs.log("CNES %s %d FALHOU: %s" % (uf, a, e))
    with open(saida, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ano", "municipio", "tipo_eqp", "situacao", "equipes"])
        for (a, mun, tp, st), n in sorted(tot.items()):
            w.writerow([a, mun, tp, st, n])
    for k in [x for x in sorted(DIAG) if x[0] == "AC"]:
        bs.log("CNES diagnostico %s: registros=%s vistos=%s desativadas=%s exemplos_DT_DESAT=%s colunas=%s" % (k, *DIAG[k]))
    bs.log("CNES: %d linhas gravadas" % len(tot))


if __name__ == "__main__":
    t0 = time.time()
    parte_cnes(os.path.join(PASTA, "CNES_EQUIPES_MUNICIPIO.csv"))
    with open(os.path.join(PASTA, "CNES_LOG.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(bs.LOG))
    print("\nPronto (%.0f min). Pode fechar." % ((time.time() - t0) / 60))
