"""
Projeto: EXPVIDA (C:\\EXPVIDA) - estudo da MIGRACAO DA VIOLENCIA por municipio (estudo separado; nao e o MISM nem o MISM3).

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva uns 20 a 30 minutos. Se parar, rode de novo.

O que faz:
  1) Rele os obitos do SIM de 2000 a 2024 e conta, ANO A ANO, por municipio de residencia, as mortes violentas
     (agressao por arma de fogo / branca / outros, intervencao legal, intencao indeterminada, suicidio, transito),
     por sexo e faixa de idade. Conta tambem os homicidios pelo municipio onde a morte OCORREU e pelo LOCAL
     (via publica, domicilio, hospital...), para separar execucao na rua de outras mortes.
  2) Baixa do Ministerio da Justica (dados.mj.gov.br) as planilhas do Sinesp com ocorrencias por municipio
     (homicidio doloso, apreensao de armas etc., 2015 em diante), para comparar policia x saude.

Grava em C:\\EXPVIDA (so contagens, nada de pessoas; nao altera arquivos existentes):
  VIOLENCIA_ANUAL_MUNICIPIO.csv     ano;municipio;sexo;faixa;causa;obitos
  HOMICIDIO_OCORRENCIA_LOCAL.csv    ano;mun_residencia;mun_ocorrencia;local;arma_fogo;obitos
  SINESP_*.xlsx / .csv              planilhas originais do Ministerio da Justica
  VIOLENCIA_LOG.txt
"""
import concurrent.futures
import csv
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request
from collections import defaultdict

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brasil_expectativa as be
import inventario_sim_ac as inv
import causas_municipio as cm

PASTA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(tempfile.gettempdir(), "expvida_violencia_cache")
LOG = []
VIOL = {"agressao_arma_fogo", "agressao_arma_branca", "agressao_outros", "intervencao_legal",
        "indeterminada_arma_fogo", "indeterminada_outros",
        "suicidio_enforcamento", "suicidio_arma_fogo", "suicidio_envenenamento", "suicidio_outros",
        "transito_pedestre", "transito_ciclista", "transito_moto", "transito_automovel", "transito_pesado", "transito_outros"}
HOMIC = {"agressao_arma_fogo", "agressao_arma_branca", "agressao_outros", "intervencao_legal"}
LOCAL = {"1": "hospital", "2": "outro_estab_saude", "3": "domicilio", "4": "via_publica", "5": "outros",
         "6": "aldeia_indigena"}


def log(m):
    print(m, flush=True)
    LOG.append(m)


def contar(dbf):
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dbf)
    pos = {nome: (a, b) for nome, a, b in cols}
    s0, s1 = pos["SEXO"]
    i0, i1 = pos["IDADE"]
    m0, m1 = pos["CODMUNRES"]
    c0, c1 = pos["CAUSABAS"]
    o01 = pos.get("CODMUNOCOR")
    l01 = pos.get("LOCOCOR")
    cont, occ = defaultdict(int), defaultdict(int)
    gi, gc = {}, {}
    base = tam_cab
    for _ in range(n_reg):
        if base + tam_reg > len(dbf):
            break
        if dbf[base] != 0x2A:
            cb = dbf[base + c0:base + c1].strip()
            c = gc.get(cb)
            if c is None:
                c = gc[cb] = cm.causa(cb)
            if c in VIOL:
                sx = dbf[base + s0:base + s1].strip().decode("latin-1")
                sx = sx if sx in ("1", "2") else "9"
                idb = dbf[base + i0:base + i1].strip()
                g = gi.get(idb)
                if g is None:
                    g = gi[idb] = be._grupo_bytes(idb)
                fx = cm.FAIXAS[cm.G2F[g]] if g >= 0 else "ign"
                mun = dbf[base + m0:base + m1].strip()[:6].decode("latin-1")
                cont[(mun, sx, fx, c)] += 1
                if c in HOMIC:
                    mo = dbf[base + o01[0]:base + o01[1]].strip()[:6].decode("latin-1") if o01 else ""
                    lo = dbf[base + l01[0]:base + l01[1]].strip().decode("latin-1") if l01 else ""
                    occ[(mun, mo, LOCAL.get(lo, "ignorado"), 1 if c == "agressao_arma_fogo" else 0)] += 1
        base += tam_reg
    return {"cont": dict(cont), "occ": dict(occ)}


def tarefa(uf, ano):
    arq = os.path.join(CACHE, "v_%s_%d.pkl" % (uf, ano))
    if os.path.exists(arq):
        return "cache"
    bruto = be._baixar(be.CAMINHO_SIM % (uf, ano))
    dbf = inv.dbc_para_dbf(bruto)
    del bruto
    be._gravar_pickle(arq, contar(dbf))
    return "ok"


def parte_sim():
    os.makedirs(CACHE, exist_ok=True)
    anos = list(range(2000, 2025))
    lista = [(uf, a) for a in anos for uf in be.UFS]
    falhas, t0 = [], time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=be.PROCESSOS) as ex:
        fut = {ex.submit(tarefa, uf, a): (uf, a) for uf, a in lista}
        for i, f in enumerate(concurrent.futures.as_completed(fut), 1):
            uf, a = fut[f]
            try:
                est = f.result()
            except Exception as e:
                falhas.append((uf, a))
                est = "FALHOU: %s" % e
            print("[%d/%d] SIM %s %d - %s (%.0f min)" % (i, len(lista), uf, a, est, (time.time() - t0) / 60), flush=True)
    if falhas:
        log("SIM: %d arquivos falharam; rode de novo. Tabelas do SIM nao gravadas." % len(falhas))
        return
    with open(os.path.join(PASTA, "VIOLENCIA_ANUAL_MUNICIPIO.csv"), "w", encoding="utf-8", newline="") as f1, \
            open(os.path.join(PASTA, "HOMICIDIO_OCORRENCIA_LOCAL.csv"), "w", encoding="utf-8", newline="") as f2:
        w1, w2 = csv.writer(f1, delimiter=";"), csv.writer(f2, delimiter=";")
        w1.writerow(["ano", "municipio", "sexo", "faixa", "causa", "obitos"])
        w2.writerow(["ano", "mun_residencia", "mun_ocorrencia", "local", "arma_fogo", "obitos"])
        for a in anos:
            c1, c2 = defaultdict(int), defaultdict(int)
            for uf in be.UFS:
                r = be._ler_pickle(os.path.join(CACHE, "v_%s_%d.pkl" % (uf, a)))
                for k, n in r["cont"].items():
                    c1[k] += n
                for k, n in r["occ"].items():
                    c2[k] += n
            for k, n in sorted(c1.items()):
                w1.writerow([a, *k, n])
            for k, n in sorted(c2.items()):
                w2.writerow([a, *k, n])
    shutil.rmtree(CACHE, ignore_errors=True)
    log("SIM anual gravado.")


def parte_sinesp():
    try:
        req = urllib.request.Request(
            "https://dados.mj.gov.br/api/3/action/package_show?id=sistema-nacional-de-estatisticas-de-seguranca-publica",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            pac = json.loads(r.read().decode("utf-8"))["result"]
    except Exception as e:
        log("Sinesp: catalogo do dados.mj.gov.br falhou: %s" % e)
        return
    for res in pac.get("resources", []):
        nome, url = res.get("name") or "", res.get("url") or ""
        log("Sinesp recurso: %s | %s" % (nome, url))
        alvo = (nome + " " + url).lower()
        if "munic" not in alvo:
            continue
        arq = "SINESP_" + os.path.basename(url.split("?")[0])
        destino = os.path.join(PASTA, arq)
        if os.path.exists(destino):
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=600) as r, open(destino + ".tmp", "wb") as f:
                shutil.copyfileobj(r, f)
            os.replace(destino + ".tmp", destino)
            log("Sinesp baixado: %s (%.1f MB)" % (arq, os.path.getsize(destino) / 1e6))
        except Exception as e:
            log("Sinesp FALHOU %s: %s" % (url, e))


if __name__ == "__main__":
    t0 = time.time()
    log("Parte 1 de 2: Sinesp (Ministerio da Justica)")
    parte_sinesp()
    log("Parte 2 de 2: SIM ano a ano")
    parte_sim()
    with open(os.path.join(PASTA, "VIOLENCIA_LOG.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    print("\nPronto (%.0f min). Pode fechar." % ((time.time() - t0) / 60))
