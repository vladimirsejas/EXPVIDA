"""
Projeto: EXPVIDA (C:\\EXPVIDA) - estudo de causas de morte por MUNICIPIO (separado do EXPVIDA principal; nao e o MISM nem o MISM3).

Como usar: abra este arquivo no VS Code e clique em "Run Python File" (o triangulo no canto de cima, a direita). Nada mais.
Leva de 1 a 2 horas. Os arquivos baixados do DATASUS ficam numa pasta temporaria do Windows (nao em C:\\EXPVIDA) e ela e
apagada no fim. Se parar no meio (queda de internet, notebook desligou), rode de novo: continua de onde parou.

O que faz: baixa do DATASUS os obitos do SIM de 2000 a 2024 (por residencia) e a populacao POPSVS, e conta, para cada
MUNICIPIO, periodo, sexo, faixa de idade e causa DETALHADA, quantos obitos houve; soma tambem as pessoas-ano por municipio.
Nenhum registro individual e guardado: so contagens.

Faixas de idade: 0 | 1-14 | 15-29 | 30-59 | 60-69 | 70-79 | 80+
Causas (CAUSABAS, CID-10), mutuamente exclusivas:
  agressao_arma_fogo X93-X95 | agressao_arma_branca X99 | agressao_outros (demais X85-Y09) | intervencao_legal Y35-Y36
  indeterminada_arma_fogo Y22-Y24 | indeterminada_outros (demais Y10-Y34)
  suicidio_enforcamento X70 | suicidio_arma_fogo X72-X74 | suicidio_envenenamento X60-X69 | suicidio_outros (demais X60-X84)
  transito_pedestre V01-V09 | transito_ciclista V10-V19 | transito_moto V20-V29 | transito_automovel V40-V49
  transito_pesado V60-V79 | transito_outros (demais V01-V99)
  afogamento W65-W74 | quedas W00-W19 | acidentes_outros (demais W00-X59) | externas_outras (demais V-Y)
  covid U07 ou B34.2 + marcador U07.1/U07.2 | infecciosas A00-B99 | neoplasias C00-D48 | diabetes E10-E14 | endocrinas_outras (demais E)
  isquemicas I20-I25 | cerebrovasculares I60-I69 | hipertensivas I10-I15 | circulatorias_outras (demais I)
  pneumonia_influenza J09-J18 | respiratorias_cronicas J40-J47 | respiratorias_outras (demais J)
  demencias F00-F03 e G30 | renais N17-N19 | alcool F10, K70, X45 | digestivas_outras (demais K)
  perinatais P | congenitas Q | mal_definidas R | outras_doencas | sem_causa

Grava em C:\\EXPVIDA (tabelas so de contagens):
  CAUSAS_MUNICIPIO.csv        periodo;municipio;sexo;faixa;causa;obitos
  POP_MUNICIPIO.csv           periodo;municipio;sexo;faixa;pessoas_ano
  CAUSAS_RACA_ESCOLARIDADE.csv periodo;microrregiao;sexo;faixa;causa_ampla;variavel;categoria;obitos
  CAUSAS_MUNICIPIO_QUALIDADE.csv uf;ano;obitos_lidos;sexo_ign;idade_ign;sem_causa;racacor_ign;esc_ign
Nao altera nenhum arquivo ja existente do EXPVIDA.
"""
import concurrent.futures
import csv
import os
import shutil
import sys
import tempfile
import time
from collections import defaultdict

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brasil_expectativa as be
import inventario_sim_ac as inv

PASTA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(tempfile.gettempdir(), "expvida_municipio_cache_v2")
PERIODOS = be.PERIODOS
ANO_PER = {a: p for p, anos in PERIODOS.items() for a in anos}
UFS = be.UFS
PROCESSOS = be.PROCESSOS

FAIXAS = ["0", "1-14", "15-29", "30-59", "60-69", "70-79", "80+"]
# grupo de 5 anos do EXPVIDA (0..17) -> faixa larga
G2F = [0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 6]

AMPLA = {}  # causa detalhada -> causa ampla (para raca/cor e escolaridade)
for c in ("agressao_arma_fogo", "agressao_arma_branca", "agressao_outros", "intervencao_legal"):
    AMPLA[c] = "agressoes"
for c in ("indeterminada_arma_fogo", "indeterminada_outros"):
    AMPLA[c] = "indeterminada"
for c in ("suicidio_enforcamento", "suicidio_arma_fogo", "suicidio_envenenamento", "suicidio_outros"):
    AMPLA[c] = "suicidio"
for c in ("transito_pedestre", "transito_ciclista", "transito_moto", "transito_automovel", "transito_pesado", "transito_outros"):
    AMPLA[c] = "transito"
for c in ("isquemicas", "cerebrovasculares", "hipertensivas", "circulatorias_outras"):
    AMPLA[c] = "circulatorias"
for c in ("neoplasias",):
    AMPLA[c] = "neoplasias"
for c in ("pneumonia_influenza", "respiratorias_cronicas", "respiratorias_outras"):
    AMPLA[c] = "respiratorias"
AMPLA["diabetes"] = "diabetes"
AMPLA["covid"] = "covid"


def causa(cb, linhas_do_atestado=()):
    """CAUSABAS (bytes, ex.: b'X954') -> causa detalhada (mutuamente exclusiva)."""
    s = cb.decode("latin-1").strip().upper()
    if len(s) < 3 or not s[0].isalpha() or not s[1:3].isdigit():
        return "sem_causa"
    L, n = s[0], int(s[1:3])
    codigo_normalizado = s.replace(".", "").replace("-", "").replace(" ", "")
    if L == "B" and n == 34:
        if isinstance(linhas_do_atestado, bool):
            marcador = linhas_do_atestado
        else:
            codigos = "".join(ch for valor in linhas_do_atestado for ch in (valor.decode("latin-1") if isinstance(valor, bytes) else str(valor)).upper() if ch.isalnum())
            marcador = "U071" in codigos or "U072" in codigos
        if marcador:
            return "covid"
    if L == "X" and 93 <= n <= 95:
        return "agressao_arma_fogo"
    if L == "X" and n == 99:
        return "agressao_arma_branca"
    if (L == "X" and n >= 85) or (L == "Y" and n <= 9):
        return "agressao_outros"
    if L == "Y" and 35 <= n <= 36:
        return "intervencao_legal"
    if L == "Y" and 22 <= n <= 24:
        return "indeterminada_arma_fogo"
    if L == "Y" and 10 <= n <= 34:
        return "indeterminada_outros"
    if L == "X" and n == 70:
        return "suicidio_enforcamento"
    if L == "X" and 72 <= n <= 74:
        return "suicidio_arma_fogo"
    if L == "X" and 60 <= n <= 69:
        return "suicidio_envenenamento"
    if L == "X" and 60 <= n <= 84:
        return "suicidio_outros"
    if L == "X" and n == 45:
        return "alcool"
    if L == "V":
        if n <= 9:
            return "transito_pedestre"
        if n <= 19:
            return "transito_ciclista"
        if 20 <= n <= 29:
            return "transito_moto"
        if 40 <= n <= 49:
            return "transito_automovel"
        if 60 <= n <= 79:
            return "transito_pesado"
        return "transito_outros"
    if L == "W" and 65 <= n <= 74:
        return "afogamento"
    if L == "W" and n <= 19:
        return "quedas"
    if L == "W" or (L == "X" and n <= 59):
        return "acidentes_outros"
    if L in "XY":
        return "externas_outras"
    if codigo_normalizado in ("U071", "U072"):
        return "covid"
    if L in "AB":
        return "infecciosas"
    if L == "C" or (L == "D" and n <= 48):
        return "neoplasias"
    if L == "E":
        return "diabetes" if 10 <= n <= 14 else "endocrinas_outras"
    if L == "I":
        if 20 <= n <= 25:
            return "isquemicas"
        if 60 <= n <= 69:
            return "cerebrovasculares"
        if 10 <= n <= 15:
            return "hipertensivas"
        return "circulatorias_outras"
    if L == "J":
        if 9 <= n <= 18:
            return "pneumonia_influenza"
        if 40 <= n <= 47:
            return "respiratorias_cronicas"
        return "respiratorias_outras"
    if (L == "F" and n <= 3) or (L == "G" and n == 30):
        return "demencias"
    if (L == "F" and n == 10) or (L == "K" and n == 70):
        return "alcool"
    if L == "N" and 17 <= n <= 19:
        return "renais"
    if L == "K":
        return "digestivas_outras"
    if L == "P":
        return "perinatais"
    if L == "Q":
        return "congenitas"
    if L == "R":
        return "mal_definidas"
    return "outras_doencas"


def _cat(valor, validos):
    v = valor.decode("latin-1").strip()
    return v if v in validos else "ignorado"


def contar(dbf):
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
    r01 = pos.get("RACACOR")
    e01 = pos.get("ESC")
    cont = defaultdict(int)
    rac = defaultdict(int)
    q = {"total": 0, "sexo_ign": 0, "idade_ign": 0, "sem_causa": 0, "racacor_ign": 0, "esc_ign": 0, "b342_com_u07": 0, "b342_sem_u07": 0, "u07_basica": 0}
    gi, gc = {}, {}
    base, fim = tam_cab, len(dbf)
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
                g = gi.get(idb)
                if g is None:
                    g = gi[idb] = be._grupo_bytes(idb)
                if g < 0:
                    q["idade_ign"] += 1
                else:
                    f = G2F[g]
                    mun = dbf[base + m0:base + m1].strip()[:6].decode("latin-1")
                    cb = dbf[base + c0:base + c1].strip()
                    marcadores = [dbf[base + a:base + b].strip() for a, b in campos_linhas]
                    tem_marcador = any("U071" in v.decode("latin-1").upper().replace(".", "").replace("-", "").replace(" ", "") or "U072" in v.decode("latin-1").upper().replace(".", "").replace("-", "").replace(" ", "") for v in marcadores)
                    cb_norm = cb.decode("latin-1").upper().replace(".", "").replace("-", "").replace(" ", "")
                    if cb_norm.startswith("B342"):
                        q["b342_com_u07" if tem_marcador else "b342_sem_u07"] += 1
                    elif cb_norm.startswith("U07"):
                        q["u07_basica"] += 1
                    chave = (cb, tem_marcador)
                    c = gc.get(chave)
                    if c is None:
                        c = gc[chave] = causa(cb, tem_marcador)
                    if c == "sem_causa":
                        q["sem_causa"] += 1
                    sxs = sx.decode("latin-1")
                    cont[(mun, sxs, f, c)] += 1
                    rc = _cat(dbf[base + r01[0]:base + r01[1]], {"1", "2", "3", "4", "5"}) if r01 else "ignorado"
                    ec = _cat(dbf[base + e01[0]:base + e01[1]], {"1", "2", "3", "4", "5"}) if e01 else "ignorado"
                    if rc == "ignorado":
                        q["racacor_ign"] += 1
                    if ec == "ignorado":
                        q["esc_ign"] += 1
                    ca = AMPLA.get(c, "outras")
                    rac[(mun, sxs, f, ca, "racacor", rc)] += 1
                    rac[(mun, sxs, f, ca, "esc", ec)] += 1
        base += tam_reg
    return {"cont": dict(cont), "rac": dict(rac), "q": q}


def tarefa(tipo, uf, ano):
    t0 = time.time()
    if tipo == "pop":
        arq = os.path.join(CACHE, "pop_%d.pkl" % ano)
        if os.path.exists(arq):
            return (tipo, uf, ano, 0.0, "cache")
        bruto = be._baixar(be.CAMINHO_POP % (ano % 100))
        if bruto is None:
            raise RuntimeError("populacao %d nao encontrada" % ano)
        be._gravar_pickle(arq, be.ler_pop_zip(bruto))
    else:
        arq = os.path.join(CACHE, "sim_%s_%d.pkl" % (uf, ano))
        if os.path.exists(arq):
            return (tipo, uf, ano, 0.0, "cache")
        bruto = be._baixar(be.CAMINHO_SIM % (uf, ano))
        if bruto is None:
            raise RuntimeError("obitos %s %d nao encontrados" % (uf, ano))
        dbf = inv.dbc_para_dbf(bruto)
        del bruto
        be._gravar_pickle(arq, contar(dbf))
    return (tipo, uf, ano, time.time() - t0, "ok")


def carregar_mapa():
    mapa = {}
    with open(os.path.join(PASTA, "MUNICIPIO_MICRORREGIAO.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            mapa[r["municipio"].strip()] = r["microrregiao"].strip()
    return mapa


def principal():
    os.makedirs(CACHE, exist_ok=True)
    mapa = carregar_mapa()
    anos = sorted(ANO_PER)
    lista = [("pop", "", a) for a in anos] + [("sim", uf, a) for a in anos for uf in UFS]
    falhas, feitos, t0 = [], 0, time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=PROCESSOS) as ex:
        fut = {ex.submit(tarefa, t, uf, a): (t, uf, a) for t, uf, a in lista}
        for f in concurrent.futures.as_completed(fut):
            feitos += 1
            t, uf, a = fut[f]
            try:
                r = f.result()
                estado = "%s %.0fs" % (r[4], r[3])
            except Exception as e:
                falhas.append((t, uf, a))
                estado = "FALHOU: %s" % e
            print("[%d/%d] %s %s %d - %s (decorrido %.0f min)" % (feitos, len(lista), t, uf, a, estado,
                                                                 (time.time() - t0) / 60), flush=True)
    if falhas:
        print("\nFalharam %d arquivos; rode de novo para tentar outra vez. Nada foi gravado." % len(falhas))
        return
    print("\nDownloads completos. Somando e gravando as tabelas ...", flush=True)
    soma, rac, pop, qual = defaultdict(int), defaultdict(int), defaultdict(float), []
    for a in anos:
        per = ANO_PER[a]
        for (mun, sx), v in be._ler_pickle(os.path.join(CACHE, "pop_%d.pkl" % a)).items():
            for g, val in enumerate(v):
                pop[(per, mun, sx, G2F[g])] += val
        for uf in UFS:
            r = be._ler_pickle(os.path.join(CACHE, "sim_%s_%d.pkl" % (uf, a)))
            for (mun, sx, fx, c), n in r["cont"].items():
                soma[(per, mun, sx, fx, c)] += n
            for (mun, sx, fx, ca, var, cat), n in r["rac"].items():
                rac[(per, mapa.get(mun, "ignorado"), sx, fx, ca, var, cat)] += n
            qq = r["q"]
            qual.append([uf, a] + [qq[k] for k in ("total", "sexo_ign", "idade_ign", "sem_causa", "racacor_ign", "esc_ign", "b342_com_u07", "b342_sem_u07", "u07_basica")])
    with open(os.path.join(PASTA, "CAUSAS_MUNICIPIO.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["periodo", "municipio", "sexo", "faixa", "causa", "obitos"])
        for (per, mun, sx, fx, c), n in sorted(soma.items()):
            w.writerow([per, mun, sx, FAIXAS[fx], c, n])
    with open(os.path.join(PASTA, "POP_MUNICIPIO.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["periodo", "municipio", "sexo", "faixa", "pessoas_ano"])
        for (per, mun, sx, fx), v in sorted(pop.items()):
            w.writerow([per, mun, sx, FAIXAS[fx], "%.1f" % v])
    with open(os.path.join(PASTA, "CAUSAS_RACA_ESCOLARIDADE.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["periodo", "microrregiao", "sexo", "faixa", "causa_ampla", "variavel", "categoria", "obitos"])
        for (per, mic, sx, fx, ca, var, cat), n in sorted(rac.items()):
            w.writerow([per, mic, sx, FAIXAS[fx], ca, var, cat, n])
    with open(os.path.join(PASTA, "CAUSAS_MUNICIPIO_QUALIDADE.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["uf", "ano", "obitos_lidos", "sexo_ign", "idade_ign", "sem_causa", "racacor_ign", "esc_ign", "b342_com_u07", "b342_sem_u07", "u07_basica"])
        w.writerows(qual)
    shutil.rmtree(CACHE, ignore_errors=True)
    print("\nPronto (%.0f min). Gravados CAUSAS_MUNICIPIO.csv, POP_MUNICIPIO.csv, CAUSAS_RACA_ESCOLARIDADE.csv e "
          "CAUSAS_MUNICIPIO_QUALIDADE.csv. Pode fechar." % ((time.time() - t0) / 60))


if __name__ == "__main__":
    principal()
