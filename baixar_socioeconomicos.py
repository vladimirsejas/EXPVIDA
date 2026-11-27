"""
Projeto: EXPVIDA (C:\\EXPVIDA) - dados socioeconomicos e de atencao primaria por MUNICIPIO (estudo separado; nao e o MISM nem o MISM3).

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva uns 20 a 40 minutos. Se parar, rode de novo.

O que baixa (so tabelas agregadas por municipio, nada de pessoas):
  1) IBGE/SIDRA: PIB municipal (tabela 5938) e populacao estimada (6579) em 2010, 2015, 2019 e 2021;
     e, do Censo 2022, as tabelas por municipio de rendimento, instrucao/alfabetizacao, saneamento (agua,
     esgoto, lixo) e Gini, localizadas automaticamente no catalogo do IBGE.
  2) DATASUS/CNES: equipes de saude (arquivos EP) ativas em dezembro de 2010, 2015, 2019, 2022 e 2024, contadas
     por municipio e tipo de equipe (para estimar a cobertura da Estrategia Saude da Familia).

Grava em C:\\EXPVIDA (nao altera nenhum arquivo existente):
  IBGE_SOCIOECONOMICO_MUNICIPIOS.csv  tabela;nome_tabela;variavel;unidade;ano;municipio;valor
  IBGE_CATALOGO_CENSO2022.csv         tabelas do Censo 2022 encontradas (para escolher outras depois)
  CNES_EQUIPES_MUNICIPIO.csv          ano;municipio;tipo_eqp;equipes
  SOCIOECONOMICOS_LOG.txt             o que deu certo e o que falhou
"""
import concurrent.futures
import csv
import json
import os
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import defaultdict

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brasil_expectativa as be
import inventario_sim_ac as inv

PASTA = os.path.dirname(os.path.abspath(__file__))
LOG = []


def log(msg):
    print(msg, flush=True)
    LOG.append(msg)


def sem_acento(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")


def get_json(url, tentativas=5):
    ultimo = None
    for t in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pesquisa academica EXPVIDA)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            ultimo = e
            time.sleep(4 * t)
    raise RuntimeError("%s -> %s" % (url, ultimo))


# ------------------------------------------------------------------ IBGE / SIDRA
def sidra(tabela, variavel, periodos):
    url = "https://apisidra.ibge.gov.br/values/t/%s/n6/all/v/%s/p/%s" % (tabela, variavel, periodos)
    dados = get_json(url)
    if not dados or len(dados) < 2:
        return []
    cab = dados[0]
    col_mun = next(k for k, v in cab.items() if k.endswith("C") and v.startswith("Munic"))
    col_var = next(k for k, v in cab.items() if k.endswith("N") and v == "Variável")
    col_ano = next((k for k, v in cab.items() if k.endswith("N") and v in ("Ano", "Período")), None)
    linhas = []
    for d in dados[1:]:
        linhas.append([d[col_var], d.get("MN", ""), d[col_ano] if col_ano else periodos, d[col_mun], d.get("V", "")])
    return linhas


def parte_ibge(saida):
    fixas = [("5938", "37", "2010,2015,2019,2021"), ("6579", "all", "2010,2015,2019,2021")]
    nomes = {"5938": "PIB dos municipios (mil reais correntes)", "6579": "Populacao residente estimada"}
    with open(saida, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["tabela", "nome_tabela", "variavel", "unidade", "ano", "municipio", "valor"])
        for t, v, p in fixas:
            try:
                ls = sidra(t, v, p)
                for l in ls:
                    w.writerow([t, nomes[t]] + l)
                log("IBGE tabela %s: %d linhas" % (t, len(ls)))
            except Exception as e:
                log("IBGE tabela %s FALHOU: %s" % (t, e))

        # Censo 2022: procura no catalogo
        try:
            cat = get_json("https://servicodados.ibge.gov.br/api/v3/agregados")
        except Exception as e:
            log("Catalogo do IBGE FALHOU: %s" % e)
            return
        chaves = ["per capita", "rendimento nominal mensal domiciliar", "gini", "alfabetiz", "nivel de instrucao",
                  "esgot", "abastecimento de agua", "lixo", "banheiro", "rendimento medio"]
        candidatos = []
        for pq in cat:
            if "censo demografico" not in sem_acento(pq.get("nome", "")):
                continue
            for ag in pq.get("agregados", []):
                n = sem_acento(ag["nome"])
                if any(k in n for k in chaves):
                    candidatos.append((ag["id"], ag["nome"]))
        log("Censo: %d tabelas candidatas no catalogo" % len(candidatos))
        achadas = []
        for tid, nome in candidatos:
            try:
                md = get_json("https://servicodados.ibge.gov.br/api/v3/agregados/%s/metadados" % tid)
            except Exception as e:
                log("metadados %s falharam: %s" % (tid, e))
                continue
            per = md.get("periodicidade", {})
            niveis = md.get("nivelTerritorial", {}).get("Administrativo", [])
            if str(per.get("fim")) != "2022" or "N6" not in niveis:
                continue
            achadas.append((tid, nome, [(str(v["id"]), v["nome"]) for v in md.get("variaveis", [])]))
        with open(os.path.join(PASTA, "IBGE_CATALOGO_CENSO2022.csv"), "w", encoding="utf-8", newline="") as fc:
            wc = csv.writer(fc, delimiter=";")
            wc.writerow(["tabela", "nome", "variaveis"])
            for tid, nome, vs in achadas:
                wc.writerow([tid, nome, " | ".join("%s=%s" % x for x in vs)])
        log("Censo 2022: %d tabelas por municipio encontradas" % len(achadas))
        for tid, nome, vs in achadas[:40]:
            for vid, vnome in vs[:12]:
                try:
                    ls = sidra(tid, vid, "2022")
                    for l in ls:
                        w.writerow([tid, nome] + l)
                except Exception as e:
                    log("Censo tabela %s variavel %s FALHOU: %s" % (tid, vid, e))
            log("Censo tabela %s ok: %s" % (tid, nome[:90]))


# ------------------------------------------------------------------ CNES equipes
CNES_ANOS = [2010, 2015, 2019, 2022, 2024]
CAMINHO_EP = "/dissemin/publicos/CNES/200508_/Dados/EP/EP%s%02d12.dbc"


def contar_ep(uf, ano):
    bruto = be._baixar(CAMINHO_EP % (uf, ano % 100))
    dbf = inv.dbc_para_dbf(bruto)
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dbf)
    pos = {nome: (a, b) for nome, a, b in cols}
    if "CODUFMUN" not in pos or "TIPO_EQP" not in pos:
        raise RuntimeError("colunas inesperadas: %s" % ",".join(pos))
    m0, m1 = pos["CODUFMUN"]
    t0, t1 = pos["TIPO_EQP"]
    d01 = pos.get("DT_DESAT")
    cont = defaultdict(int)
    base = tam_cab
    for _ in range(n_reg):
        if base + tam_reg > len(dbf):
            break
        if dbf[base] != 0x2A:
            ativa = True
            if d01:
                ativa = dbf[base + d01[0]:base + d01[1]].strip() == b""
            if ativa:
                mun = dbf[base + m0:base + m1].strip()[:6].decode("latin-1")
                tp = dbf[base + t0:base + t1].strip().decode("latin-1")
                cont[(mun, tp)] += 1
        base += tam_reg
    return dict(cont)


def parte_cnes(saida):
    tot = defaultdict(int)
    tarefas = [(uf, a) for a in CNES_ANOS for uf in be.UFS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        fut = {ex.submit(contar_ep, uf, a): (uf, a) for uf, a in tarefas}
        for i, f in enumerate(concurrent.futures.as_completed(fut), 1):
            uf, a = fut[f]
            try:
                for (mun, tp), n in f.result().items():
                    tot[(a, mun, tp)] += n
                print("[%d/%d] CNES %s %d ok" % (i, len(tarefas), uf, a), flush=True)
            except Exception as e:
                log("CNES %s %d FALHOU: %s" % (uf, a, e))
    with open(saida, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ano", "municipio", "tipo_eqp", "equipes"])
        for (a, mun, tp), n in sorted(tot.items()):
            w.writerow([a, mun, tp, n])
    log("CNES: %d linhas gravadas" % len(tot))


if __name__ == "__main__":
    t0 = time.time()
    log("Parte 1 de 2: IBGE")
    parte_ibge(os.path.join(PASTA, "IBGE_SOCIOECONOMICO_MUNICIPIOS.csv"))
    log("Parte 2 de 2: CNES (equipes de saude)")
    parte_cnes(os.path.join(PASTA, "CNES_EQUIPES_MUNICIPIO.csv"))
    with open(os.path.join(PASTA, "SOCIOECONOMICOS_LOG.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    print("\nPronto (%.0f min). Pode fechar." % ((time.time() - t0) / 60))
