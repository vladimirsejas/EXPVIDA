"""
Projeto: EXPVIDA (C:\\EXPVIDA) - complemento socioeconomico enxuto do Censo 2022 + equipes CNES.

Como usar: abra este arquivo no VS Code e clique em "Run Python File" SOMENTE depois que o
baixar_violencia.py mostrar "Pronto". Leva uns 15 a 40 minutos.

O que faz:
  1) Para cada tabela do Censo 2022 escolhida (renda, alfabetizacao, saneamento), le os metadados
     no IBGE, abre a classificacao principal (todas as categorias) e fixa as demais no "Total".
     Grava CENSO2022_SOCIO_MUNICIPIOS.csv (tabela;nome_tabela;variavel;unidade;categoria;municipio;valor).
  2) Conta as equipes de saude ativas por municipio no CNES (2010, 2015, 2019, 2022, 2024)
     e grava CNES_EQUIPES_MUNICIPIO.csv.
  3) Grava CENSO2022_LOG.txt.
Nao altera nenhum arquivo que ja existe na pasta (exceto se CNES_EQUIPES_MUNICIPIO.csv ja existir).
"""
import csv
import os
import time
import unicodedata

import baixar_socioeconomicos as bs

PASTA = os.path.dirname(os.path.abspath(__file__))

TABELAS = [
    "10295",  # rendimento domiciliar per capita (valores)
    "10296",  # moradores por classes de rendimento per capita (em salarios minimos)
    "10297",  # composicao do rendimento domiciliar (trabalho, beneficios etc.)
    "10281",  # rendimento medio e mediano do trabalho
    "9543",   # taxa de alfabetizacao
    "6803",   # ligacao a rede geral de agua
    "6805",   # tipo de esgotamento sanitario
    "6892",   # destino do lixo
    "6806",   # banheiro de uso exclusivo
]


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def escolher_classificacoes(md):
    """Classificacao com mais categorias fica aberta (em blocos); as outras ficam no Total.
    Devolve uma lista de filtros; cada um pede no maximo ~8 categorias para nao passar do limite do SIDRA."""
    cls = md.get("classificacoes", [])
    if not cls:
        return [""]
    principal = max(cls, key=lambda c: len(c.get("categorias", [])))
    fixos = []
    for c in cls:
        if c is principal:
            continue
        cats = c.get("categorias", [])
        tot = next((k for k in cats if sem_acento(k["nome"]).startswith("total")), cats[0] if cats else None)
        if tot is not None:
            fixos.append("c%s/%s" % (c["id"], tot["id"]))
    ids = [str(k["id"]) for k in principal.get("categorias", [])]
    blocos = [ids[i:i + 8] for i in range(0, len(ids), 8)] or [[]]
    return ["/" + "/".join(["c%s/%s" % (principal["id"], ",".join(b))] + fixos) for b in blocos]


def baixar_tabela(tid, w):
    md = bs.get_json("https://servicodados.ibge.gov.br/api/v3/agregados/%s/metadados" % tid)
    nome = md.get("nome", "")
    niveis = md.get("nivelTerritorial", {}).get("Administrativo", [])
    if "N6" not in niveis:
        bs.log("Tabela %s sem nivel municipal, pulada" % tid)
        return
    total = 0
    for v in md.get("variaveis", []):
      for filtro in escolher_classificacoes(md):
        url = "https://apisidra.ibge.gov.br/values/t/%s/n6/all/v/%s/p/2022%s" % (tid, v["id"], filtro)
        try:
            dados = bs.get_json(url, tentativas=2)
        except Exception as e:
            bs.log("Tabela %s variavel %s FALHOU: %s" % (tid, v["id"], e))
            continue
        if not dados or len(dados) < 2:
            continue
        cab = dados[0]
        col_mun = next(k for k, x in cab.items() if k.endswith("C") and x.startswith("Munic"))
        col_var = next(k for k, x in cab.items() if k.endswith("N") and x == "Variável")
        ignorar = {"Município", "Variável", "Ano", "Período", "Brasil, Grande Região e Unidade da Federação"}
        cols_cat = [k for k, x in cab.items() if k.endswith("N") and k.startswith("D") and x not in ignorar
                    and not x.startswith("Munic")]
        for d in dados[1:]:
            cat = " | ".join(d[k] for k in cols_cat)
            w.writerow([tid, nome, d[col_var], d.get("MN", ""), cat, d[col_mun], d.get("V", "")])
            total += 1
        time.sleep(1)
    bs.log("Tabela %s ok (%d linhas): %s" % (tid, total, nome[:90]))


if __name__ == "__main__":
    t0 = time.time()
    bs.log("Parte 1 de 2: Censo 2022 (renda, alfabetizacao, saneamento)")
    with open(os.path.join(PASTA, "CENSO2022_SOCIO_MUNICIPIOS.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["tabela", "nome_tabela", "variavel", "unidade", "categoria", "municipio", "valor"])
        for tid in TABELAS:
            try:
                baixar_tabela(tid, w)
            except Exception as e:
                bs.log("Tabela %s FALHOU: %s" % (tid, e))
            f.flush()
    cnes = os.path.join(PASTA, "CNES_EQUIPES_MUNICIPIO.csv")
    if os.path.exists(cnes) and os.path.getsize(cnes) > 1000:
        bs.log("Parte 2 de 2: CNES ja baixado antes, pulado")
    else:
        bs.log("Parte 2 de 2: CNES (equipes de saude)")
        bs.parte_cnes(cnes)
    with open(os.path.join(PASTA, "CENSO2022_LOG.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(bs.LOG))
    print("\nPronto (%.0f min). Pode fechar." % ((time.time() - t0) / 60))
