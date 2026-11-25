"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
BRASIL INTEIRO: expectativa de vida e mortalidade por idade, por municipio, microrregiao, UF e Brasil, por sexo.

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Nada mais.
Se o computador desligar ou o programa parar, rode de novo: o que ja foi baixado fica guardado numa
pasta temporaria do Windows (nao em C:\\EXPVIDA) e o programa continua de onde parou.
Ao terminar com sucesso, a pasta temporaria e apagada.

O que faz:
  1. Baixa do DATASUS a populacao (IBGE/POPSVS, por municipio, sexo e idade) e os obitos do SIM
     (um arquivo por UF e ano, por residencia), de 2000 a 2024, em varios processos ao mesmo tempo.
  2. Soma os anos de cada periodo e constroi tabuas de vida abreviadas por sexo para cada municipio,
     microrregiao (IBGE, pela tabela CADMUN do DATASUS), UF e Brasil.
  3. Calcula incerteza por simulacao (obitos como contagens de Poisson) e descreve a desigualdade
     entre microrregioes, por idade.
  4. Grava na pasta do script: BRASIL_municipios.csv, BRASIL_microrregioes.csv, BRASIL_ufs_e_brasil.csv,
     BRASIL_taxas_por_idade.csv, BRASIL_RESUMO.md e BRASIL_PROGRESSO.txt.

Regras do projeto: so dados publicos baixados do DATASUS; nada e imputado nem inventado; obitos com sexo,
idade ou municipio ignorados sao contados e relatados; nenhum registro individual e gravado em disco.
"""
import concurrent.futures
import csv
import io
import math
import os
import pickle
import random
import shutil
import sys
import tempfile
import time
import zipfile
from collections import defaultdict

sys.dont_write_bytecode = True  # nao criar a pasta __pycache__
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario_sim_ac as inv      # descompactacao .dbc e leitura de DBF
import piloto_expectativa as pil     # tabua de vida, Poisson, percentis, FTP

# ------------------------------------------------------------------ CONFIGURACAO
ANOS_SIM = tuple(range(2000, 2025))          # obitos: 2000 a 2024
PERIODOS = {
    "2000-2004": (2000, 2001, 2002, 2003, 2004),
    "2005-2009": (2005, 2006, 2007, 2008, 2009),
    "2010-2014": (2010, 2011, 2012, 2013, 2014),
    "2015-2019": (2015, 2016, 2017, 2018, 2019),
    "2020-2021 pandemia": (2020, 2021),
    "2022-2024": (2022, 2023, 2024),
}
# UFs na ordem aproximada de tamanho do arquivo (as maiores primeiro, para equilibrar o trabalho)
UFS = ["SP", "MG", "RJ", "BA", "RS", "PR", "PE", "CE", "PA", "SC", "GO", "MA", "PB", "ES", "PI",
       "AL", "RN", "AM", "MT", "MS", "DF", "SE", "RO", "TO", "AC", "AP", "RR"]
PROCESSOS = max(1, min(4, (os.cpu_count() or 2) - 1))   # processos simultaneos (4 no maximo, para poupar memoria)
SIMS_MUNICIPIO = 100        # simulacoes por municipio (so quando ha obitos suficientes)
SIMS_AGREGADO = 200         # simulacoes por microrregiao, UF e Brasil
SEMENTE = 20261124
LIMITE_INSTAVEL = 100       # menos obitos que isso no periodo e sexo = unidade instavel
MIN_OBITOS_TAXA = 20        # para comparar taxas por idade entre microrregioes
APAGAR_CACHE = True
# ------------------------------------------------------------------------------

PASTA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(tempfile.gettempdir(), "expvida_cache")
SIGLA = {v: k for k, v in pil.COD_UF.items()}
NG = pil.NG
ROTULO_IDADE = ["0", "1-4"] + ["%d-%d" % (a, a + 4) for a in range(5, 80, 5)] + ["80+"]
NOME_SEXO = {"1": "homens", "2": "mulheres"}
CAMINHO_POP = "/dissemin/publicos/IBGE/POPSVS/POPSBR%02d.zip"
CAMINHO_SIM = "/dissemin/publicos/SIM/CID10/DORES/DO%s%d.dbc"
CAMINHO_CADMUN = "/dissemin/publicos/SIM/CID10/TABELAS/CADMUN.DBF"


# ------------------------------------------------------------------ utilidades
def _gravar_pickle(caminho, obj):
    tmp = caminho + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(obj, f, protocol=4)
    os.replace(tmp, caminho)


def _ler_pickle(caminho):
    with open(caminho, "rb") as f:
        return pickle.load(f)


def _grupo_bytes(idb):
    """Idade do SIM (3 caracteres) -> grupo etario, ou -1 se ignorada."""
    s = idb.decode("latin-1").strip()
    if len(s) != 3 or not s.isdigit() or s[0] == "9":
        return -1
    u, v = s[0], int(s[1:])
    anos = v if u == "4" else (100 + v if u == "5" else 0)   # 0 a 3 = menos de 1 ano
    return pil.grupo_da_idade(anos)


def _baixar(caminho):
    ultimo = None
    for tentativa in range(1, 5):
        try:
            ftp = pil.ftp_conectar()
            try:
                return pil.baixar_bytes(ftp, caminho)
            finally:
                try:
                    ftp.quit()
                except Exception:
                    ftp.close()
        except Exception as e:  # rede instavel: espera e tenta de novo
            ultimo = e
            time.sleep(5 * tentativa)
    raise RuntimeError("falha ao baixar %s: %s" % (caminho, ultimo))


# ------------------------------------------------------------------ leitura dos dados
def contar_sim(dbf):
    """Conta obitos por (municipio, sexo, grupo de idade). Nao guarda nenhum registro individual."""
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dbf)
    pos = {nome: (a, b) for nome, a, b in cols}
    s0, s1 = pos["SEXO"]
    i0, i1 = pos["IDADE"]
    m0, m1 = pos["CODMUNRES"]
    cont = defaultdict(int)
    ign = {"total": 0, "sexo": 0, "idade": 0}
    grupos = {}
    base = tam_cab
    fim = len(dbf)
    for _ in range(n_reg):
        if base + tam_reg > fim:
            break
        if dbf[base] != 0x2A:                       # registro nao apagado
            ign["total"] += 1
            sx = dbf[base + s0:base + s1].strip()   # ate 2017 o campo vem com espacos ("1   ")
            if sx != b"1" and sx != b"2":
                ign["sexo"] += 1
            else:
                idb = dbf[base + i0:base + i1].strip()
                g = grupos.get(idb)
                if g is None:
                    g = grupos[idb] = _grupo_bytes(idb)
                if g < 0:
                    ign["idade"] += 1
                else:
                    cont[(dbf[base + m0:base + m1].strip()[:6], sx, g)] += 1   # 7 digitos em anos antigos
        base += tam_reg
    cont = {(m.decode("latin-1"), s.decode("latin-1"), g): n for (m, s, g), n in cont.items()}
    return {"cont": cont, "ign": ign}


def ler_pop_zip(bruto):
    """Zip do POPSVS -> {(municipio6, sexo): [pessoas por grupo etario]}."""
    with zipfile.ZipFile(io.BytesIO(bruto)) as z:
        dados = z.read(z.namelist()[0])
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dados)
    pos = {nome: (a, b) for nome, a, b in cols}
    (c0, c1), (s0, s1), (i0, i1), (p0, p1) = pos["COD_MUN"], pos["SEXO"], pos["IDADE"], pos["POP"]
    pop = defaultdict(lambda: [0.0] * NG)
    base = tam_cab
    for _ in range(n_reg):
        if base + tam_reg > len(dados):
            break
        mun = dados[base + c0:base + c1].decode("latin-1").strip()[:6]
        sexo = dados[base + s0:base + s1].decode("latin-1").strip()
        if sexo in ("1", "2"):
            idade = int(dados[base + i0:base + i1].decode("latin-1").strip())
            valor = float(dados[base + p0:base + p1].decode("latin-1").strip().replace(",", "."))
            pop[(mun, sexo)][pil.grupo_da_idade(idade)] += valor
        base += tam_reg
    return dict(pop)


def tarefa(tipo, uf, ano, cache):
    """Executada em processo separado. Devolve (tipo, uf, ano, segundos, estado)."""
    t0 = time.time()
    if tipo == "pop":
        arq = os.path.join(cache, "pop_%d.pkl" % ano)
        if os.path.exists(arq):
            return (tipo, uf, ano, 0.0, "cache")
        bruto = _baixar(CAMINHO_POP % (ano % 100))
        if bruto is None:
            raise RuntimeError("populacao %d nao encontrada" % ano)
        _gravar_pickle(arq, ler_pop_zip(bruto))
    else:
        arq = os.path.join(cache, "sim_%s_%d.pkl" % (uf, ano))
        if os.path.exists(arq):
            return (tipo, uf, ano, 0.0, "cache")
        bruto = _baixar(CAMINHO_SIM % (uf, ano))
        if bruto is None:
            raise RuntimeError("obitos %s %d nao encontrados" % (uf, ano))
        dbf = inv.dbc_para_dbf(bruto)
        del bruto
        _gravar_pickle(arq, contar_sim(dbf))
    return (tipo, uf, ano, time.time() - t0, "ok")


def carregar_cadmun(cache):
    arq = os.path.join(cache, "cadmun.pkl")
    if os.path.exists(arq):
        return _ler_pickle(arq)
    bruto = _baixar(CAMINHO_CADMUN)
    if bruto is None:
        raise RuntimeError("CADMUN nao encontrado")
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(bruto)
    pos = {nome: (a, b) for nome, a, b in cols}
    campo = lambda reg, nome: reg[pos[nome][0]:pos[nome][1]].decode("latin-1").strip()
    cad = {}
    for k in range(n_reg):
        reg = bruto[tam_cab + k * tam_reg: tam_cab + (k + 1) * tam_reg]
        if len(reg) < tam_reg or reg[0:1] == b"*":
            continue
        cad[campo(reg, "MUNCOD")[:6]] = {"nome": campo(reg, "MUNNOMEX"), "uf": campo(reg, "UFCOD"),
                                         "micro": campo(reg, "MICROCOD")}
    _gravar_pickle(arq, cad)
    return cad


# ------------------------------------------------------------------ execucao paralela
def _progresso(texto):
    with open(os.path.join(PASTA, "BRASIL_PROGRESSO.txt"), "w", encoding="utf-8") as f:
        f.write(texto + "\n")


def baixar_tudo(cache, ufs, anos):
    lista = [("pop", "", a) for a in anos] + [("sim", uf, a) for uf in ufs for a in anos]
    total = len(lista)
    feitos, falhas = 0, []
    t0 = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=PROCESSOS) as ex:
        futuros = {ex.submit(tarefa, t, uf, a, cache): (t, uf, a) for t, uf, a in lista}
        for fut in concurrent.futures.as_completed(futuros):
            t, uf, a = futuros[fut]
            feitos += 1
            try:
                r = fut.result()
                estado = "%s %.0fs" % (r[4], r[3])
            except Exception as e:
                falhas.append((t, uf, a, str(e)))
                estado = "FALHOU: %s" % e
            msg = "[%d/%d] %s %s %d - %s (decorrido %.0f min)" % (feitos, total, t, uf, a, estado, (time.time() - t0) / 60)
            print(msg, flush=True)
            _progresso(msg + ("\nFalhas ate agora: %d" % len(falhas) if falhas else ""))
    return falhas


# ------------------------------------------------------------------ agregacao e tabuas
def _somar(destino, origem):
    for i in range(NG):
        destino[i] += origem[i]


def agregar_periodo(cache, ufs, anos, cad):
    """Soma obitos e pessoas-ano do periodo. Devolve (D_mun, PY_mun, D_extra_uf, ign)."""
    PY = defaultdict(lambda: [0.0] * NG)
    for ano in anos:
        for chave, v in _ler_pickle(os.path.join(cache, "pop_%d.pkl" % ano)).items():
            _somar(PY[chave], v)
    conhecidos = {m for (m, s) in PY}
    D = defaultdict(lambda: [0] * NG)
    extra = defaultdict(lambda: [0] * NG)          # obitos sem municipio valido: contam so no total da UF
    ign = {"total": 0, "sexo": 0, "idade": 0, "municipio": 0}
    for uf in ufs:
        for ano in anos:
            r = _ler_pickle(os.path.join(cache, "sim_%s_%d.pkl" % (uf, ano)))
            for k in ("total", "sexo", "idade"):
                ign[k] += r["ign"][k]
            for (mun, sexo, g), n in r["cont"].items():
                if mun in conhecidos:
                    D[(mun, sexo)][g] += n
                else:
                    extra[(uf, sexo)][g] += n
                    ign["municipio"] += n
    return D, PY, extra, ign


def simular(D, PY, sexo, nsim, rng):
    e0s, e80 = [], []
    for _ in range(nsim):
        t = pil.tabua([pil.poisson(d, rng) for d in D], PY, sexo)
        if t:
            e0s.append(t["e0"])
            e80.append(t["e0_80"])
    return pil.percentis(e0s), pil.percentis(e80)


CAMPOS = ["nivel", "codigo", "nome", "uf", "periodo", "sexo", "obitos", "pessoas_ano", "e0", "e0_ic_inf", "e0_ic_sup",
          "e0_80", "e0_80_ic_inf", "e0_80_ic_sup", "e15", "e60", "q0", "q15_60", "instavel"]


def calcular(nivel, codigo, nome, uf, periodo, sexo, D, PY, nsim, rng):
    obitos = int(sum(D))
    r = {"nivel": nivel, "codigo": codigo, "nome": nome, "uf": uf, "periodo": periodo, "sexo": sexo,
         "obitos": obitos, "pessoas_ano": sum(PY), "instavel": 1 if obitos < LIMITE_INSTAVEL else 0}
    t = pil.tabua(D, PY, sexo)
    if t is None:
        return r, None
    r.update({"e0": t["e0"], "e0_80": t["e0_80"], "e15": t["e15"], "e60": t["e60"],
              "q0": t["q0"], "q15_60": t["q15_60"]})
    if nsim and obitos >= LIMITE_INSTAVEL:
        (a, b), (c, d) = simular(D, PY, sexo, nsim, rng)
        r.update({"e0_ic_inf": a, "e0_ic_sup": b, "e0_80_ic_inf": c, "e0_80_ic_sup": d})
    return r, t


def _fmt(v):
    if isinstance(v, float):
        return "" if v != v else ("%.4f" % v)
    return v


def pct(valores, p):
    v = sorted(valores)
    if not v:
        return float("nan")
    i = (len(v) - 1) * p
    lo = int(i)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def agregar_e_gravar(cache, cad, ufs, periodos, pasta, sims_mun=SIMS_MUNICIPIO, sims_agr=SIMS_AGREGADO):
    rng = random.Random(SEMENTE)
    saidas = {"mun": [], "micro": [], "uf": []}
    taxas = []                         # linhas BRASIL_taxas_por_idade.csv
    res = {}                           # (nivel, periodo, sexo, codigo) -> dict de resultados
    taxas_micro = {}                   # (periodo, sexo) -> {micro: (D, PY)}
    ignorados = {}
    nome_micro = {}
    for p_idx, (periodo, anos) in enumerate(periodos.items()):
        _progresso("Agregando periodo %s (%d de %d)" % (periodo, p_idx + 1, len(periodos)))
        print("Agregando periodo", periodo, flush=True)
        D, PY, extra, ign = agregar_periodo(cache, ufs, anos, cad)
        ignorados[periodo] = ign
        # --- microrregioes e UFs
        micro_D = defaultdict(lambda: [0] * NG)
        micro_PY = defaultdict(lambda: [0.0] * NG)
        uf_D = defaultdict(lambda: [0] * NG)
        uf_PY = defaultdict(lambda: [0.0] * NG)
        maior = {}
        for (mun, sexo), py in PY.items():
            info = cad.get(mun)
            micro = info["micro"] if info and info["micro"] and not info["micro"].endswith("000") else None
            ufc = mun[:2]
            _somar(uf_PY[(ufc, sexo)], py)
            if micro:
                _somar(micro_PY[(micro, sexo)], py)
                tot = sum(py)
                if tot > maior.get(micro, (0, ""))[0]:
                    maior[micro] = (tot, mun)
        for (mun, sexo), d in D.items():
            info = cad.get(mun)
            micro = info["micro"] if info and info["micro"] and not info["micro"].endswith("000") else None
            _somar(uf_D[(mun[:2], sexo)], d)
            if micro:
                _somar(micro_D[(micro, sexo)], d)
        for (uf, sexo), d in extra.items():
            _somar(uf_D[(pil.COD_UF[uf], sexo)], d)
        for micro, (tot, mun) in maior.items():
            nome_micro[micro] = "Microrregião de %s" % cad[mun]["nome"].title()
        # --- municipios
        for (mun, sexo) in sorted(PY):
            info = cad.get(mun, {"nome": mun, "uf": mun[:2]})
            d = D.get((mun, sexo), [0] * NG)
            r, t = calcular("municipio", mun, info["nome"].title(), SIGLA.get(mun[:2], mun[:2]), periodo, sexo,
                            d, PY[(mun, sexo)], sims_mun, rng)
            saidas["mun"].append(r)
        # --- microrregioes
        tm = {}
        for (micro, sexo), py in sorted(micro_PY.items()):
            d = micro_D.get((micro, sexo), [0] * NG)
            r, t = calcular("microrregiao", micro, nome_micro.get(micro, micro), SIGLA.get(micro[:2], micro[:2]),
                            periodo, sexo, d, py, sims_agr, rng)
            saidas["micro"].append(r)
            res[("micro", periodo, sexo, micro)] = r
            tm.setdefault(sexo, {})[micro] = (d, py)
            for g in range(NG):
                taxas.append(["microrregiao", micro, periodo, sexo, pil.INICIO[g], d[g], "%.2f" % py[g]])
        for sexo, dic in tm.items():
            taxas_micro[(periodo, sexo)] = dic
        # --- UFs e Brasil
        br_D = {"1": [0] * NG, "2": [0] * NG}
        br_PY = {"1": [0.0] * NG, "2": [0.0] * NG}
        for (ufc, sexo), py in sorted(uf_PY.items()):
            if ufc not in SIGLA:
                continue
            d = uf_D.get((ufc, sexo), [0] * NG)
            r, t = calcular("uf", ufc, SIGLA[ufc], SIGLA[ufc], periodo, sexo, d, py, sims_agr, rng)
            saidas["uf"].append(r)
            res[("uf", periodo, sexo, ufc)] = r
            _somar(br_D[sexo], d)
            _somar(br_PY[sexo], py)
            for g in range(NG):
                taxas.append(["uf", SIGLA[ufc], periodo, sexo, pil.INICIO[g], d[g], "%.2f" % py[g]])
        for sexo in ("1", "2"):
            r, t = calcular("brasil", "BR", "Brasil", "BR", periodo, sexo, br_D[sexo], br_PY[sexo], sims_agr, rng)
            saidas["uf"].append(r)
            res[("brasil", periodo, sexo, "BR")] = r
            for g in range(NG):
                taxas.append(["brasil", "BR", periodo, sexo, pil.INICIO[g], br_D[sexo][g], "%.2f" % br_PY[sexo][g]])

    # --- CSV
    def gravar_csv(nome, linhas, campos):
        with open(os.path.join(pasta, nome), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(campos)
            for r in linhas:
                w.writerow([_fmt(r.get(c, "")) for c in campos] if isinstance(r, dict) else r)
    gravar_csv("BRASIL_municipios.csv", saidas["mun"], CAMPOS)
    gravar_csv("BRASIL_microrregioes.csv", saidas["micro"], CAMPOS)
    gravar_csv("BRASIL_ufs_e_brasil.csv", saidas["uf"], CAMPOS)
    gravar_csv("BRASIL_taxas_por_idade.csv", taxas,
               ["nivel", "codigo", "periodo", "sexo", "idade_inicio", "obitos", "pessoas_ano"])
    escrever_resumo(pasta, periodos, res, taxas_micro, ignorados, saidas, nome_micro, ufs)


# ------------------------------------------------------------------ resumo
def escrever_resumo(pasta, periodos, res, taxas_micro, ignorados, saidas, nome_micro, ufs):
    nomes = list(periodos)
    L = []
    L.append("# Brasil inteiro: expectativa de vida e mortalidade por idade, por sexo e território\n")
    L.append("Gerado por brasil_expectativa.py (projeto \"Quando o território importa\", pasta C:\\EXPVIDA). "
             "Dados públicos do DATASUS: óbitos do SIM por residência, %d a %d, e população do IBGE/POPSVS por município, "
             "sexo e idade. Tábuas de vida abreviadas por sexo, com óbitos e pessoas-ano somados em cada janela. "
             "Incerteza (IC 95%%) por simulação de Poisson, considerando só os óbitos (a incerteza da população não entra). "
             "Resultados descritivos e ecológicos: descrevem territórios, não indivíduos, e não provam causa.\n"
             % (min(min(a) for a in periodos.values()), max(max(a) for a in periodos.values())))
    L.append("e0 = expectativa de vida ao nascer. e0-80 = anos vividos entre 0 e 80 anos (robusta quando há poucos óbitos). "
             "Unidade \"instável\" = menos de %d óbitos naquele sexo e período.\n" % LIMITE_INSTAVEL)

    L.append("## Brasil\n")
    L.append("| Período | Sexo | Óbitos | e0 (IC 95%) | e0-80 (IC 95%) | q15-60 | q0 por mil |")
    L.append("|---|---|---|---|---|---|---|")
    for p in nomes:
        for sx in ("1", "2"):
            r = res.get(("brasil", p, sx, "BR"))
            if r and "e0" in r:
                L.append("| %s | %s | %d | %.1f (%.1f a %.1f) | %.1f (%.1f a %.1f) | %.3f | %.1f |" % (
                    p, NOME_SEXO[sx], r["obitos"], r["e0"], r.get("e0_ic_inf", float("nan")), r.get("e0_ic_sup", float("nan")),
                    r["e0_80"], r.get("e0_80_ic_inf", float("nan")), r.get("e0_80_ic_sup", float("nan")),
                    r["q15_60"], 1000 * r["q0"]))
    L.append("")

    ref, pan, dep = "2015-2019", "2020-2021 pandemia", "2022-2024"
    L.append("## e0 por UF e período\n")
    L.append("As duas últimas colunas são a diferença em anos de e0 em relação a 2015-2019 (pandemia e depois dela).\n")
    for sx in ("1", "2"):
        L.append("### %s\n" % NOME_SEXO[sx].capitalize())
        L.append("| UF | " + " | ".join(nomes) + " | Δ pandemia | Δ 2022-24 |")
        L.append("|---|" + "---|" * (len(nomes) + 2))
        for ufc in sorted(SIGLA):
            cel, ok = [], True
            vals = {}
            for p in nomes:
                r = res.get(("uf", p, sx, ufc))
                if r and "e0" in r:
                    vals[p] = r["e0"]
                    cel.append("%.1f" % r["e0"])
                else:
                    cel.append("-")
            dp = "%+.1f" % (vals[pan] - vals[ref]) if pan in vals and ref in vals else "-"
            dd = "%+.1f" % (vals[dep] - vals[ref]) if dep in vals and ref in vals else "-"
            L.append("| %s | %s | %s | %s |" % (SIGLA[ufc], " | ".join(cel), dp, dd))
        L.append("")

    L.append("## Desigualdade entre microrregiões (sem peso por população)\n")
    L.append("Cada linha resume a distribuição de e0 e e0-80 entre as microrregiões do IBGE com ao menos %d óbitos no sexo "
             "e no período. P10, P50 e P90 são os percentis 10, 50 e 90; a amplitude é P90 menos P10, em anos.\n" % LIMITE_INSTAVEL)
    L.append("| Período | Sexo | Microrregiões | e0-80 P10 | P50 | P90 | amplitude | e0 P10 | P50 | P90 | amplitude |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for p in nomes:
        for sx in ("1", "2"):
            rs = [r for (n, pp, s, c), r in res.items() if n == "micro" and pp == p and s == sx
                  and "e0" in r and r["obitos"] >= LIMITE_INSTAVEL]
            if not rs:
                continue
            a = [r["e0_80"] for r in rs]
            b = [r["e0"] for r in rs]
            L.append("| %s | %s | %d | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f |" % (
                p, NOME_SEXO[sx], len(rs), pct(a, .1), pct(a, .5), pct(a, .9), pct(a, .9) - pct(a, .1),
                pct(b, .1), pct(b, .5), pct(b, .9), pct(b, .9) - pct(b, .1)))
    L.append("")

    L.append("## Extremos entre microrregiões em %s (e0-80)\n" % ref)
    for sx in ("1", "2"):
        rs = sorted([r for (n, pp, s, c), r in res.items() if n == "micro" and pp == ref and s == sx
                     and "e0_80" in r and r["obitos"] >= LIMITE_INSTAVEL], key=lambda r: r["e0_80"])
        if len(rs) < 10:
            continue
        L.append("### %s\n" % NOME_SEXO[sx].capitalize())
        L.append("| Posição | Microrregião | UF | e0-80 | Óbitos |")
        L.append("|---|---|---|---|---|")
        for r in rs[:5]:
            L.append("| menores | %s | %s | %.1f | %d |" % (r["nome"], r["uf"], r["e0_80"], r["obitos"]))
        for r in rs[-5:]:
            L.append("| maiores | %s | %s | %.1f | %d |" % (r["nome"], r["uf"], r["e0_80"], r["obitos"]))
        L.append("")

    L.append("## Desigualdade por idade entre microrregiões\n")
    L.append("Taxa de mortalidade por mil pessoas em cada faixa etária, entre microrregiões com ao menos %d óbitos na faixa. "
             "A razão é P90 dividido por P10: quantas vezes a taxa do território no 90º percentil supera a do 10º. "
             "Isto responde onde, na vida, a desigualdade territorial é maior, e se a pandemia a alterou por idade.\n" % MIN_OBITOS_TAXA)
    for sx in ("1", "2"):
        L.append("### %s\n" % NOME_SEXO[sx].capitalize())
        L.append("| Idade | Microrregiões (%s) | Taxa P10 (%s) | P50 | P90 | Razão P90/P10 %s | %s | %s |" % (
            ref, ref, ref, pan, dep))
        L.append("|---|---|---|---|---|---|---|---|")
        for g in range(NG):
            linha = []
            for p in (ref, pan, dep):
                dic = taxas_micro.get((p, sx), {})
                tx = [1000.0 * d[g] / py[g] for (d, py) in dic.values() if d[g] >= MIN_OBITOS_TAXA and py[g] > 0]
                linha.append(tx)
            base = linha[0]
            if len(base) < 10:
                L.append("| %s | %d | - | - | - | - | - | - |" % (ROTULO_IDADE[g], len(base)))
                continue
            def razao(tx):
                return "%.2f" % (pct(tx, .9) / pct(tx, .1)) if len(tx) >= 10 and pct(tx, .1) > 0 else "-"
            L.append("| %s | %d | %.2f | %.2f | %.2f | %s | %s | %s |" % (
                ROTULO_IDADE[g], len(base), pct(base, .1), pct(base, .5), pct(base, .9),
                razao(linha[0]), razao(linha[1]), razao(linha[2])))
        L.append("")

    L.append("## Óbitos lidos e excluídos por período\n")
    L.append("Óbitos com sexo ou idade ignorados saem de todas as tábuas. Óbitos com município de residência não identificado "
             "(por exemplo, código terminado em 0000) ficam fora dos municípios e das microrregiões, mas entram nos totais da UF e do Brasil.\n")
    L.append("| Período | Lidos | Sexo ignorado | Idade ignorada | Município não identificado |")
    L.append("|---|---|---|---|---|")
    for p in nomes:
        g = ignorados[p]
        L.append("| %s | %d | %d | %d | %d |" % (p, g["total"], g["sexo"], g["idade"], g["municipio"]))
    L.append("")

    n_mun = {}
    for r in saidas["mun"]:
        k = (r["periodo"], r["sexo"])
        n_mun.setdefault(k, [0, 0])
        n_mun[k][0] += 1
        n_mun[k][1] += r["instavel"]
    L.append("## Municípios instáveis\n")
    L.append("| Período | Sexo | Municípios | Instáveis (menos de %d óbitos) |" % LIMITE_INSTAVEL)
    L.append("|---|---|---|---|")
    for p in nomes:
        for sx in ("1", "2"):
            if (p, sx) in n_mun:
                L.append("| %s | %s | %d | %d |" % (p, NOME_SEXO[sx], n_mun[(p, sx)][0], n_mun[(p, sx)][1]))
    L.append("")

    L.append("## Limites\n")
    L.append("O sub-registro de óbitos e a qualidade da causa e da idade foram maiores no início dos anos 2000 e em municípios pequenos "
             "e pobres, o que tende a elevar a expectativa de vida aparente desses lugares; este é um limite dos dados, não corrigido aqui. "
             "As populações do IBGE (POPSVS) são estimativas que foram revisadas com os censos, e o ajuste de períodos distintos pode mudar tendências. "
             "A incerteza mostrada vem só da variação aleatória dos óbitos. Microrregião é a divisão do IBGE vigente na tabela CADMUN do DATASUS. "
             "A idade média ao morrer não é expectativa de vida, e as comparações entre territórios são ecológicas: "
             "mostram associação entre lugares, nunca causa para pessoas. "
             "A associação com o CEP, pedida pelo professor, ainda não foi feita: aqui o menor recorte é o município.\n")
    with open(os.path.join(pasta, "BRASIL_RESUMO.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ principal
def principal():
    t0 = time.time()
    os.makedirs(CACHE, exist_ok=True)
    print("Pasta temporaria de trabalho:", CACHE, "| processos:", PROCESSOS, flush=True)
    _progresso("Iniciando")
    cad = carregar_cadmun(CACHE)
    print("CADMUN: %d municipios" % len(cad), flush=True)
    falhas = baixar_tudo(CACHE, UFS, ANOS_SIM)
    if falhas:
        texto = "TERMINOU COM %d FALHAS. Rode o script de novo: o que ja foi baixado nao sera baixado outra vez.\n" % len(falhas)
        texto += "\n".join("%s %s %s: %s" % f for f in falhas[:50])
        print(texto, flush=True)
        _progresso(texto)
        return
    agregar_e_gravar(CACHE, cad, UFS, PERIODOS, PASTA)
    minutos = (time.time() - t0) / 60
    _progresso("CONCLUIDO em %.0f minutos. Resultados: BRASIL_RESUMO.md e os CSV BRASIL_*." % minutos)
    print("Concluido em %.0f minutos." % minutos, flush=True)
    if APAGAR_CACHE:
        shutil.rmtree(CACHE, ignore_errors=True)


if __name__ == "__main__":
    principal()
