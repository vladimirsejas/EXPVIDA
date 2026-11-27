"""
Projeto: Quando o territorio importa (C:\\EXPVIDA) - ESTUDO 2, CAUSAS DE MORTE (separado do EXPVIDA principal).

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Nada mais.
Leva cerca de 20 minutos. Os arquivos baixados ficam numa pasta temporaria do Windows (nao em C:\\EXPVIDA) e
ela e apagada ao final. Se parar no meio, rode de novo: continua de onde parou.

O que faz: baixa do DATASUS os obitos do SIM de 2015 a 2019 (um arquivo por UF e ano, por residencia) e conta,
para cada microrregiao, sexo, faixa de idade (as mesmas 18 do EXPVIDA) e GRUPO DE CAUSA, quantos obitos houve.
Os grupos sao mutuamente exclusivos (cada obito entra em um so), pela causa basica (CAUSABAS, CID-10):
  agressoes X85-Y09 | intervencao_legal Y35-Y36 | suicidio X60-X84 | transporte V01-V99 |
  intencao_indeterminada Y10-Y34 | acidentes_outros W00-X59 | externas_outras (demais V-Y) |
  infecciosas A00-B99 | neoplasias C00-D48 | endocrinas_nutricionais E00-E90 | circulatorias I00-I99 |
  respiratorias J00-J99 | digestivas K00-K93 | perinatais P00-P96 | congenitas Q00-Q99 |
  mal_definidas R00-R99 | outras_doencas (todo o resto) | sem_causa (campo vazio ou invalido)
A ligacao municipio-microrregiao vem de MUNICIPIO_MICRORREGIAO.csv (na mesma pasta; criado por
tabela_municipio_microrregiao.py).

Grava na pasta do script, SO DUAS TABELAS PEQUENAS (nenhum registro individual e guardado):
  CAUSAS_OBITOS_2015_2019.csv   microrregiao;sexo;idade_inicio;causa;obitos
  CAUSAS_QUALIDADE.csv          por UF e ano: total de obitos lidos, ignorados por sexo, idade e municipio, sem causa
Nao altera nenhum arquivo do EXPVIDA. Nao envia nada para a internet alem do download do DATASUS.
"""
import concurrent.futures
import csv
import os
import sys
import tempfile
import time
from collections import defaultdict

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brasil_expectativa as be
import inventario_sim_ac as inv

PASTA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(tempfile.gettempdir(), "expvida_causas_cache_v2")
ANOS = (2015, 2016, 2017, 2018, 2019)
UFS = be.UFS
PROCESSOS = be.PROCESSOS
CAMINHO_SIM = be.CAMINHO_SIM
GRUPOS = ["agressoes", "intervencao_legal", "suicidio", "transporte", "intencao_indeterminada", "acidentes_outros",
          "externas_outras", "covid19", "infecciosas", "neoplasias", "endocrinas_nutricionais", "circulatorias", "respiratorias",
          "digestivas", "perinatais", "congenitas", "mal_definidas", "outras_doencas", "sem_causa"]


def grupo_causa(cb, linhas_do_atestado=()):
    """Classifica causa basica; COVID exige B34.2 e marcador U07.1/U07.2."""
    s = cb.decode("latin-1").strip().upper()
    if len(s) < 3 or not s[0].isalpha() or not s[1:3].isdigit():
        return "sem_causa"
    L, n = s[0], int(s[1:3])
    codigo_normalizado = s.replace(".", "").replace("-", "").replace(" ", "")
    if codigo_normalizado in ("U071", "U072"):
        return "covid19"
    if L == "B" and n == 34:
        if isinstance(linhas_do_atestado, bool):
            marcador = linhas_do_atestado
        else:
            codigos = "".join(ch for valor in linhas_do_atestado for ch in (valor.decode("latin-1") if isinstance(valor, bytes) else str(valor)).upper() if ch.isalnum())
            marcador = "U071" in codigos or "U072" in codigos
        if marcador:
            return "covid19"
    if L in "VWXY":
        if L == "X" and 60 <= n <= 84:
            return "suicidio"
        if (L == "X" and n >= 85) or (L == "Y" and n <= 9):
            return "agressoes"
        if L == "Y" and 10 <= n <= 34:
            return "intencao_indeterminada"
        if L == "Y" and 35 <= n <= 36:
            return "intervencao_legal"
        if L == "V":
            return "transporte"
        if (L == "W") or (L == "X" and n <= 59):
            return "acidentes_outros"
        return "externas_outras"
    if L in "AB":
        return "infecciosas"
    if L == "C" or (L == "D" and n <= 48):
        return "neoplasias"
    if L == "E":
        return "endocrinas_nutricionais"
    if L == "I":
        return "circulatorias"
    if L == "J":
        return "respiratorias"
    if L == "K":
        return "digestivas"
    if L == "P":
        return "perinatais"
    if L == "Q":
        return "congenitas"
    if L == "R":
        return "mal_definidas"
    return "outras_doencas"


def carregar_mapa():
    caminho = os.path.join(PASTA, "MUNICIPIO_MICRORREGIAO.csv")
    if not os.path.exists(caminho):
        raise SystemExit("Falta MUNICIPIO_MICRORREGIAO.csv na pasta do script (rode antes tabela_municipio_microrregiao.py).")
    mapa = {}
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            mapa[r["municipio"].strip()] = r["microrregiao"].strip()
    return mapa


def contar(dbf, mapa):
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dbf)
    pos = {nome: (a, b) for nome, a, b in cols}
    for nome in ("SEXO", "IDADE", "CODMUNRES", "CAUSABAS", "LINHAA", "LINHAB", "LINHAC", "LINHAD", "LINHAII"):
        if nome not in pos:
            raise RuntimeError("coluna %s ausente no arquivo" % nome)
    s0, s1 = pos["SEXO"]
    i0, i1 = pos["IDADE"]
    m0, m1 = pos["CODMUNRES"]
    c0, c1 = pos["CAUSABAS"]
    campos_linhas = [pos[n] for n in ("LINHAA", "LINHAB", "LINHAC", "LINHAD", "LINHAII")]
    cont = defaultdict(int)
    q = {"total": 0, "sexo_ign": 0, "idade_ign": 0, "municipio_ign": 0, "sem_causa": 0, "b342_com_u07": 0, "b342_sem_u07": 0, "u07_basica": 0}
    grupos_idade, grupos_causa = {}, {}
    base = tam_cab
    fim = len(dbf)
    for _ in range(n_reg):
        if base + tam_reg > fim:
            break
        if dbf[base] != 0x2A:
            q["total"] += 1
            sx = dbf[base + s0:base + s1].strip()
            if sx != b"1" and sx != b"2":
                q["sexo_ign"] += 1
            else:
                idb = dbf[base + i0:base + i1].strip()
                g = grupos_idade.get(idb)
                if g is None:
                    g = grupos_idade[idb] = be._grupo_bytes(idb)
                if g < 0:
                    q["idade_ign"] += 1
                else:
                    mun = dbf[base + m0:base + m1].strip()[:6].decode("latin-1")
                    mic = mapa.get(mun)
                    if mic is None:
                        q["municipio_ign"] += 1
                    else:
                        cb = dbf[base + c0:base + c1].strip()
                        marcadores = [dbf[base + a:base + b].strip() for a, b in campos_linhas]
                        tem_marcador = any("U071" in v.decode("latin-1").upper().replace(".", "").replace("-", "").replace(" ", "") or "U072" in v.decode("latin-1").upper().replace(".", "").replace("-", "").replace(" ", "") for v in marcadores)
                        cb_norm = cb.decode("latin-1").upper().replace(".", "").replace("-", "").replace(" ", "")
                        if cb_norm.startswith("B342"):
                            q["b342_com_u07" if tem_marcador else "b342_sem_u07"] += 1
                        elif cb_norm.startswith("U07"):
                            q["u07_basica"] += 1
                        chave = (cb, tem_marcador)
                        gc = grupos_causa.get(chave)
                        if gc is None:
                            gc = grupos_causa[chave] = grupo_causa(cb, tem_marcador)
                        if gc == "sem_causa":
                            q["sem_causa"] += 1
                        cont[(mic, sx.decode("latin-1"), g, gc)] += 1
        base += tam_reg
    return {"cont": dict(cont), "q": q}


def tarefa(uf, ano):
    t0 = time.time()
    arq = os.path.join(CACHE, "causas_%s_%d.pkl" % (uf, ano))
    if os.path.exists(arq):
        return (uf, ano, 0.0, "cache")
    bruto = be._baixar(CAMINHO_SIM % (uf, ano))
    if bruto is None:
        raise RuntimeError("obitos %s %d nao encontrados" % (uf, ano))
    dbf = inv.dbc_para_dbf(bruto)
    del bruto
    be._gravar_pickle(arq, contar(dbf, carregar_mapa()))
    return (uf, ano, time.time() - t0, "ok")


def principal():
    os.makedirs(CACHE, exist_ok=True)
    carregar_mapa()  # falha cedo se faltar o arquivo
    lista = [(uf, a) for uf in UFS for a in ANOS]
    falhas, feitos, t0 = [], 0, time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=PROCESSOS) as ex:
        fut = {ex.submit(tarefa, uf, a): (uf, a) for uf, a in lista}
        for f in concurrent.futures.as_completed(fut):
            feitos += 1
            uf, a = fut[f]
            try:
                r = f.result()
                estado = "%s %.0fs" % (r[3], r[2])
            except Exception as e:
                falhas.append((uf, a, str(e)))
                estado = "FALHOU: %s" % e
            print("[%d/%d] %s %d - %s (decorrido %.0f min)" % (feitos, len(lista), uf, a, estado, (time.time() - t0) / 60), flush=True)
    if falhas:
        print("\nFalharam %d arquivos; rode de novo para tentar outra vez. Nada foi gravado." % len(falhas))
        return
    soma = defaultdict(int)
    qual = []
    for uf, a in lista:
        r = be._ler_pickle(os.path.join(CACHE, "causas_%s_%d.pkl" % (uf, a)))
        for k, v in r["cont"].items():
            soma[k] += v
        qual.append([uf, a] + [r["q"][c] for c in ("total", "sexo_ign", "idade_ign", "municipio_ign", "sem_causa", "b342_com_u07", "b342_sem_u07", "u07_basica")])
    with open(os.path.join(PASTA, "CAUSAS_OBITOS_2015_2019.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["microrregiao", "sexo", "idade_inicio", "causa", "obitos"])
        for (mic, sx, g, gc), n in sorted(soma.items()):
            w.writerow([mic, sx, inv_idade(g), gc, n])
    with open(os.path.join(PASTA, "CAUSAS_QUALIDADE.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["uf", "ano", "obitos_lidos", "sexo_ignorado", "idade_ignorada", "municipio_ignorado", "sem_causa", "b342_com_u07", "b342_sem_u07", "u07_basica"])
        w.writerows(qual)
    import shutil
    shutil.rmtree(CACHE, ignore_errors=True)
    print("\nPronto. Gravados CAUSAS_OBITOS_2015_2019.csv e CAUSAS_QUALIDADE.csv. Pode fechar.")


def inv_idade(g):
    return ([0, 1] + list(range(5, 85, 5)))[g]


if __name__ == "__main__":
    principal()
