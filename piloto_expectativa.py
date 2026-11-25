"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
PILOTO: expectativa de vida e mortalidade por idade, por municipio e sexo.

Para ampliar para outro estado ou para o Brasil, mude apenas as linhas de CONFIGURACAO abaixo.

O que faz:
  1. Baixa os obitos do SIM (DO<UF><ano>.dbc) e a populacao (POPSVS, por municipio, sexo e idade simples).
  2. Soma os anos do periodo (obitos e pessoas-ano) para reduzir a instabilidade de numeros pequenos.
  3. Constroi tabuas de vida abreviadas por municipio e sexo.
  4. Calcula incerteza por simulacao (obitos tratados como contagens de Poisson).
  5. Grava PILOTO_<UF>_municipios.csv e PILOTO_<UF>_RESUMO.md na pasta do script.

Regras: so dados publicos baixados do DATASUS (nada fica em disco alem dos resultados);
obitos com sexo, idade ou municipio ignorados sao contados e relatados, sem imputacao;
nenhum registro individual e gravado.
"""
import csv
import ftplib
import io
import math
import os
import random
import struct
import sys
import tempfile
import zipfile
from collections import defaultdict

sys.dont_write_bytecode = True  # nao criar a pasta __pycache__
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario_sim_ac as inv  # download FTP, descompactacao .dbc e leitura de DBF

# ------------------------------------------------------------------ CONFIGURACAO
UF = "AC"                      # sigla do estado (para o Brasil inteiro, rodar uma vez por UF)
PERIODOS = {                   # janelas somadas e comparadas; 2020-2021 (pandemia) fica separada
    "2000-2004": (2000, 2001, 2002, 2003, 2004),
    "2005-2009": (2005, 2006, 2007, 2008, 2009),
    "2010-2014": (2010, 2011, 2012, 2013, 2014),
    "2015-2019": (2015, 2016, 2017, 2018, 2019),
    "2020-2021 pandemia": (2020, 2021),
    "2022-2024": (2022, 2023, 2024),
}
ANOS = ()                      # preenchido automaticamente para cada periodo
NOME = ""
SIMULACOES = 300               # numero de simulacoes para a incerteza
SEMENTE = 20261124             # semente do sorteio, para o resultado ser reproduzivel
LIMITE_OBITOS_INSTAVEL = 100   # abaixo disso, no periodo e no sexo, o municipio e marcado como instavel
# ------------------------------------------------------------------------------

COD_UF = {"RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17",
          "MA": "21", "PI": "22", "CE": "23", "RN": "24", "PB": "25", "PE": "26", "AL": "27",
          "SE": "28", "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35", "PR": "41",
          "SC": "42", "RS": "43", "MS": "50", "MT": "51", "GO": "52", "DF": "53"}
PASTA = os.path.dirname(os.path.abspath(__file__))

# grupos de idade: 0, 1-4, 5-9, ..., 75-79, 80+
INICIO = [0, 1] + list(range(5, 85, 5))
LARG = [1, 4] + [5] * 15 + [None]       # None = intervalo aberto (80 e mais)
NG = len(INICIO)


def grupo_da_idade(anos):
    if anos >= 80:
        return NG - 1
    if anos == 0:
        return 0
    if anos < 5:
        return 1
    return 2 + (anos - 5) // 5


# ------------------------------------------------------------------ tabua de vida
def tabua(D, PY, sexo):
    """D, PY: listas por grupo de idade. Devolve dict com indicadores, ou None se nao calculavel."""
    if PY[0] <= 0 or PY[-1] <= 0 or any(p <= 0 for p in PY):
        return None
    m = [D[i] / PY[i] for i in range(NG)]
    a = [None] * NG
    m0 = m[0]
    if sexo == "1":
        a[0] = 0.330 if m0 >= 0.107 else 0.045 + 2.684 * m0
        a[1] = 1.352 if m0 >= 0.107 else 1.651 - 2.816 * m0
    else:
        a[0] = 0.350 if m0 >= 0.107 else 0.053 + 2.800 * m0
        a[1] = 1.361 if m0 >= 0.107 else 1.522 - 1.518 * m0
    for i in range(2, NG - 1):
        a[i] = LARG[i] / 2.0
    q = [0.0] * NG
    for i in range(NG - 1):
        n = LARG[i]
        q[i] = min(1.0, n * m[i] / (1.0 + (n - a[i]) * m[i]))
    q[-1] = 1.0
    l = [1.0] * NG
    for i in range(1, NG):
        l[i] = l[i - 1] * (1.0 - q[i - 1])
    L = [0.0] * NG
    for i in range(NG - 1):
        n = LARG[i]
        L[i] = n * l[i + 1] + a[i] * (l[i] - l[i + 1])
    if m[-1] <= 0:
        return None
    L[-1] = l[-1] / m[-1]
    T = [0.0] * NG
    T[-1] = L[-1]
    for i in range(NG - 2, -1, -1):
        T[i] = T[i + 1] + L[i]

    def e(i):
        return T[i] / l[i] if l[i] > 0 else float("nan")

    i15, i40, i60 = INICIO.index(15), INICIO.index(40), INICIO.index(60)
    return {
        "e0_80": sum(L[:-1]) / l[0],                 # anos vividos entre 0 e 80 (nao depende da faixa 80+)
        "q0": q[0],                                  # probabilidade de morrer antes de 1 ano
        "q1_4": q[1],                                # entre 1 e 5 anos
        "q15_60": 1.0 - l[INICIO.index(60)] / l[i15],  # entre 15 e 60 anos
        "e0": e(0), "e15": e(i15), "e40": e(i40), "e60": e(i60),
    }


def poisson(lam, rng):
    if lam <= 0:
        return 0
    if lam < 30:
        limite, k, p = math.exp(-lam), 0, 1.0
        while True:
            p *= rng.random()
            if p <= limite:
                return k
            k += 1
    return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))


def percentis(valores):
    v = sorted(x for x in valores if x == x)
    if len(v) < 20:
        return (float("nan"), float("nan"))
    return (v[int(0.025 * (len(v) - 1))], v[int(0.975 * (len(v) - 1))])


# ------------------------------------------------------------------ dados
def ftp_conectar():
    ftp = ftplib.FTP(inv.SERVIDOR, timeout=300)
    ftp.login()
    ftp.set_pasv(True)
    return ftp


def baixar_bytes(ftp, caminho):
    buf = io.BytesIO()
    try:
        ftp.retrbinary("RETR " + caminho, buf.write)
    except ftplib.error_perm as e:
        if str(e).startswith("550"):
            return None
        raise
    return buf.getvalue()


def obitos(dbf, pops_mun, acum, ign):
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dbf)
    pos = {nome: (a, b) for nome, a, b in cols}
    (s0, s1), (i0, i1), (m0, m1) = pos["SEXO"], pos["IDADE"], pos["CODMUNRES"]
    for k in range(n_reg):
        reg = dbf[tam_cab + k * tam_reg: tam_cab + (k + 1) * tam_reg]
        if len(reg) < tam_reg or reg[0:1] == b"*":
            continue
        sexo = reg[s0:s1].decode("latin-1").strip()
        idade = reg[i0:i1].decode("latin-1").strip()
        mun = reg[m0:m1].decode("latin-1").strip()[:6]  # anos antigos tem 7 digitos (com verificador)
        ign["total"] += 1
        if sexo not in ("1", "2"):
            ign["sexo"] += 1
            continue
        if len(idade) != 3 or not idade.isdigit() or idade[0] == "9":
            ign["idade"] += 1
            continue
        if mun not in pops_mun:
            ign["municipio"] += 1
            continue
        u, v = idade[0], int(idade[1:])
        anos = v if u == "4" else (100 + v if u == "5" else 0)  # 0 a 3 = menos de 1 ano
        acum[(mun, sexo)][grupo_da_idade(anos)] += 1


def ler_populacao(ftp, ano, prefixo, acum_py, municipios):
    yy = ano % 100
    bruto = baixar_bytes(ftp, "/dissemin/publicos/IBGE/POPSVS/POPSBR%02d.zip" % yy)
    if bruto is None:
        raise RuntimeError("populacao %d nao encontrada" % ano)
    with zipfile.ZipFile(io.BytesIO(bruto)) as z:
        dados = z.read(z.namelist()[0])
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dados)
    pos = {nome: (a, b) for nome, a, b in cols}
    (c0, c1), (s0, s1), (i0, i1), (p0, p1) = pos["COD_MUN"], pos["SEXO"], pos["IDADE"], pos["POP"]
    for k in range(n_reg):
        reg = dados[tam_cab + k * tam_reg: tam_cab + (k + 1) * tam_reg]
        cod = reg[c0:c1].decode("latin-1").strip()
        if not cod.startswith(prefixo):
            continue
        mun = cod[:6]                      # remove o digito verificador (7 -> 6 digitos)
        sexo = reg[s0:s1].decode("latin-1").strip()
        idade = int(reg[i0:i1].decode("latin-1").strip())
        pop = float(reg[p0:p1].decode("latin-1").strip().replace(",", "."))
        municipios.add(mun)
        acum_py[(mun, sexo)][grupo_da_idade(idade)] += pop


def rodar():
    rng = random.Random(SEMENTE)
    prefixo = COD_UF[UF]
    municipios = set()
    PY = defaultdict(lambda: [0.0] * NG)
    D = defaultdict(lambda: [0] * NG)
    ign = defaultdict(int)
    print("Conectando ao DATASUS ...")
    ftp = ftp_conectar()
    try:
        for ano in ANOS:
            print("Populacao %d ..." % ano, flush=True)
            ler_populacao(ftp, ano, prefixo, PY, municipios)
        for ano in ANOS:
            print("Obitos %s %d ..." % (UF, ano), flush=True)
            bruto = baixar_bytes(ftp, "/dissemin/publicos/SIM/CID10/DORES/DO%s%d.dbc" % (UF, ano))
            if bruto is None:
                raise RuntimeError("obitos %s %d nao encontrados" % (UF, ano))
            obitos(inv.dbc_para_dbf(bruto), municipios, D, ign)
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()

    linhas = []
    unidades = sorted(municipios) + ["TOTAL_" + UF]
    for un in unidades:
        for sexo in ("1", "2"):
            if un.startswith("TOTAL_"):
                d = [sum(D[(m, sexo)][i] for m in municipios) for i in range(NG)]
                py = [sum(PY[(m, sexo)][i] for m in municipios) for i in range(NG)]
            else:
                d, py = D[(un, sexo)], PY[(un, sexo)]
            tot_d = sum(d)
            res = tabua(d, py, sexo)
            if res is None:
                linhas.append({"unidade": un, "sexo": sexo, "obitos": tot_d, "pessoas_ano": round(sum(py)),
                               "instavel": "sim", "nota": "tabua nao calculavel (grupo sem populacao ou sem obitos em 80+)"})
                continue
            sims = {k: [] for k in ("q0", "q15_60", "e0", "e60", "e0_80")}
            for _ in range(SIMULACOES):
                ds = [poisson(x, rng) for x in d]
                r = tabua(ds, py, sexo)
                if r:
                    for k in sims:
                        sims[k].append(r[k])
            ic = {k: percentis(v) for k, v in sims.items()}
            linhas.append({
                "unidade": un, "sexo": sexo, "obitos": tot_d, "pessoas_ano": round(sum(py)),
                "q0": res["q0"], "q0_ic_inf": ic["q0"][0], "q0_ic_sup": ic["q0"][1],
                "q1_4": res["q1_4"],
                "q15_60": res["q15_60"], "q15_60_ic_inf": ic["q15_60"][0], "q15_60_ic_sup": ic["q15_60"][1],
                "e0": res["e0"], "e0_ic_inf": ic["e0"][0], "e0_ic_sup": ic["e0"][1],
                "e0_80": res["e0_80"], "e0_80_ic_inf": ic["e0_80"][0], "e0_80_ic_sup": ic["e0_80"][1],
                "e15": res["e15"], "e40": res["e40"],
                "e60": res["e60"], "e60_ic_inf": ic["e60"][0], "e60_ic_sup": ic["e60"][1],
                "instavel": "sim" if tot_d < LIMITE_OBITOS_INSTAVEL else "nao", "nota": ""})

    campos = ["unidade", "sexo", "obitos", "pessoas_ano", "q0", "q0_ic_inf", "q0_ic_sup", "q1_4",
              "q15_60", "q15_60_ic_inf", "q15_60_ic_sup", "e0", "e0_ic_inf", "e0_ic_sup",
              "e0_80", "e0_80_ic_inf", "e0_80_ic_sup", "e15", "e40", "e60", "e60_ic_inf", "e60_ic_sup", "instavel", "nota"]
    return linhas, campos, ign, municipios


NOMES_AC = {
    "120001": "Acrelandia", "120005": "Assis Brasil", "120010": "Brasileia", "120013": "Bujari",
    "120017": "Capixaba", "120020": "Cruzeiro do Sul", "120025": "Epitaciolandia", "120030": "Feijo",
    "120032": "Jordao", "120033": "Manoel Urbano", "120034": "Marechal Thaumaturgo",
    "120035": "Mancio Lima", "120038": "Placido de Castro", "120039": "Porto Walter",
    "120040": "Rio Branco", "120042": "Rodrigues Alves", "120043": "Santa Rosa do Purus",
    "120045": "Senador Guiomard", "120050": "Sena Madureira", "120060": "Tarauaca",
    "120070": "Xapuri", "120080": "Porto Acre",
}


def rotulo(cod):
    return "%s (%s)" % (NOMES_AC[cod], cod) if cod in NOMES_AC else cod


def principal():
    global ANOS, NOME
    todas, totais, ignorados, campos = [], {}, {}, None
    for nome, anos in PERIODOS.items():
        ANOS, NOME = anos, nome
        print("=== Periodo %s ===" % nome, flush=True)
        linhas, campos, ign, mun = rodar()
        ignorados[nome] = dict(ign)
        for r in linhas:
            r["periodo"] = nome
            todas.append(r)
        totais[nome] = [r for r in linhas if r["unidade"].startswith("TOTAL_") and "e0" in r]

    caminho = os.path.join(PASTA, "PILOTO_%s_municipios_periodos.csv" % UF)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["periodo"] + campos, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in todas:
            w.writerow({k: ("%.4f" % v if isinstance(v, float) else v) for k, v in r.items()})

    L = ["# Comparacao entre periodos: %s\n" % UF]
    L.append("Gerado por piloto_expectativa.py. Tabuas de vida abreviadas por municipio e sexo; obitos e pessoas-ano "
             "somados em cada janela. Incerteza (IC 95%%) por simulacao de Poisson com %d repeticoes, considerando so os obitos. "
             "Numeros do piloto de teste do metodo, nao conclusoes.\n" % SIMULACOES)
    L.append("e0 = expectativa de vida ao nascer. e0-80 = anos vividos entre 0 e 80 anos (robusta em municipio pequeno). "
             "q15-60 = probabilidade de morrer entre 15 e 60 anos. q0 = mortalidade no primeiro ano, por mil.\n")
    L.append("## Total do estado\n")
    L.append("| Periodo | Sexo | Obitos | e0 (IC 95%) | e0-80 (IC 95%) | q15-60 | q0 |")
    L.append("|---|---|---|---|---|---|---|")
    for nome in PERIODOS:
        for r in totais[nome]:
            L.append("| %s | %s | %d | %.1f (%.1f a %.1f) | %.1f (%.1f a %.1f) | %.3f | %.1f |" % (
                nome, "homens" if r["sexo"] == "1" else "mulheres", r["obitos"],
                r["e0"], r["e0_ic_inf"], r["e0_ic_sup"], r["e0_80"], r["e0_80_ic_inf"], r["e0_80_ic_sup"],
                r["q15_60"], 1000 * r["q0"]))
    L.append("\n## Anos vividos entre 0 e 80 (e0-80), por municipio e periodo\n")
    L.append("Asterisco: menos de %d obitos naquele sexo e periodo; leitura com cautela. "
             "Os intervalos de cada numero estao no CSV.\n" % LIMITE_OBITOS_INSTAVEL)
    por = defaultdict(dict)
    for r in todas:
        if not r["unidade"].startswith("TOTAL_"):
            por[(r["unidade"], r["sexo"])][r["periodo"]] = r
    for sx, titulo in (("1", "Homens"), ("2", "Mulheres")):
        L.append("### %s\n" % titulo)
        L.append("| Municipio | " + " | ".join(PERIODOS) + " |")
        L.append("|---|" + "---|" * len(PERIODOS))
        for un in sorted({u for (u, s_) in por if s_ == sx}):
            cel = []
            for nome in PERIODOS:
                r = por[(un, sx)].get(nome)
                if r is None or "e0_80" not in r:
                    cel.append("-")
                else:
                    cel.append("%.1f%s" % (r["e0_80"], "*" if r["obitos"] < LIMITE_OBITOS_INSTAVEL else ""))
            L.append("| %s | %s |" % (rotulo(un), " | ".join(cel)))
        L.append("")
    L.append("## Obitos excluidos por periodo\n")
    L.append("| Periodo | Lidos | Sexo ignorado | Idade ignorada | Municipio fora da lista |")
    L.append("|---|---|---|---|---|")
    for nome in PERIODOS:
        g = ignorados[nome]
        L.append("| %s | %d | %d | %d | %d |" % (nome, g.get("total", 0), g.get("sexo", 0), g.get("idade", 0), g.get("municipio", 0)))
    L.append("\n## Limites\n")
    L.append("- Ecologico: municipios, nao individuos. Associacao nao e causalidade.")
    L.append("- Subregistro de obitos nao e corrigido; ele tende a ser maior nos primeiros anos da serie (anos 2000) e em municipios pequenos, o que pode subestimar a mortalidade e superestimar a expectativa de vida.")
    L.append("- Populacao: estimativas do Ministerio da Saude/IBGE, que mudam a cada revisao e nao entram na incerteza.")
    L.append("- Para idade 0 e 1 a 4 anos, a distribuicao dos obitos dentro do grupo usa as formulas de Coale e Demeny (Preston, Heuveline e Guillot, 2001); nos demais grupos, o ponto medio.")
    with open(os.path.join(PASTA, "PILOTO_%s_COMPARACAO_PERIODOS.md" % UF), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("Pronto. Gravei PILOTO_%s_municipios_periodos.csv e PILOTO_%s_COMPARACAO_PERIODOS.md em %s" % (UF, UF, PASTA))


if __name__ == "__main__":
    principal()
