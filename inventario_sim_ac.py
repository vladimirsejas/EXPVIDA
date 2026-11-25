"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
Inventario do SIM (Sistema de Informacoes sobre Mortalidade) do Acre.

O que faz:
  1. Baixa, ano a ano, o arquivo publico de obitos do Acre (DOAC<ano>.dbc) do DATASUS (FTP).
  2. Descompacta (.dbc -> .dbf) com codigo proprio, sem instalar nada.
  3. Mede, por ano, quais colunas existem e quanto cada uma esta preenchida.
  4. Grava dois arquivos na mesma pasta do script:
       - INVENTARIO_SIM_AC.md  (resumo para ler)
       - inventario_sim_ac_colunas.csv  (coluna x ano, preenchimento)

Regras: so dados publicos baixados do DATASUS. Nenhum registro individual e gravado:
os arquivos de saida trazem apenas contagens e percentuais. Os arquivos baixados
ficam numa pasta temporaria e sao apagados ao final (nao ocupam disco).
"""
import csv
import os
import struct
import sys
import tempfile
import ftplib
from collections import Counter

SERVIDOR = "ftp.datasus.gov.br"
CAMINHO = "/dissemin/publicos/SIM/CID10/DORES/DOAC{ano}.dbc"
ANOS = range(2000, 2025)
PASTA = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- descompactacao
# Metodo "PKWare DCL implode", o mesmo que o DATASUS usa nos arquivos .dbc.
_LITLEN = [11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8, 23, 8, 9, 7, 6, 7, 8,
           7, 6, 55, 8, 23, 24, 12, 11, 7, 9, 11, 12, 6, 7, 22, 5, 7, 24, 6, 11, 9, 6, 7, 22, 7,
           11, 38, 7, 9, 8, 25, 11, 8, 11, 9, 12, 8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10,
           53, 8, 7, 24, 10, 27, 44, 253, 253, 253, 252, 252, 252, 13, 12, 45, 12, 45, 12, 61, 12,
           45, 44, 173]
_LENLEN = [2, 35, 36, 53, 38, 23]
_DISTLEN = [2, 20, 53, 230, 247, 151, 248]
_BASE = [3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264]
_EXTRA = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]


def _construir(rep, n):
    comprimentos = []
    for b in rep:
        repete = (b >> 4) + 1
        comp = b & 15
        comprimentos.extend([comp] * repete)
    assert len(comprimentos) == n
    count = [0] * 16
    for c in comprimentos:
        count[c] += 1
    offs = [0] * 16
    for i in range(1, 15):
        offs[i + 1] = offs[i] + count[i]
    simbolos = [0] * n
    for s, c in enumerate(comprimentos):
        if c:
            simbolos[offs[c]] = s
            offs[c] += 1
    return count, simbolos


_LIT = _construir(_LITLEN, 256)
_LEN = _construir(_LENLEN, 16)
_DIST = _construir(_DISTLEN, 64)


class _Bits:
    def __init__(self, dados, pos):
        self.d, self.p, self.buf, self.cnt = dados, pos, 0, 0

    def bits(self, need):
        val = self.buf
        while self.cnt < need:
            val |= self.d[self.p] << self.cnt
            self.p += 1
            self.cnt += 8
        self.buf = val >> need
        self.cnt -= need
        return val & ((1 << need) - 1)

    def decode(self, tabela):
        count, simbolos = tabela
        code = first = index = 0
        for comp in range(1, 16):
            code |= self.bits(1) ^ 1
            c = count[comp]
            if code < first + c:
                return simbolos[index + (code - first)]
            index += c
            first = (first + c) << 1
            code <<= 1
        raise ValueError("codigo invalido")


# --- descompactacao rapida (mesmo metodo, com tabelas de consulta em vez de leitura bit a bit)
def _tabela_rapida(tab):
    count, simbolos = tab
    comp_max = max(L for L in range(1, 16) if count[L])
    entradas = []
    first = index = 0
    for L in range(1, 16):
        c = count[L]
        for k in range(c):
            cod = first + k
            sym = simbolos[index + k]
            padrao = 0
            for i in range(L):
                padrao |= (((cod >> (L - 1 - i)) & 1) ^ 1) << i
            entradas.append((padrao, L, sym))
        index += c
        first = (first + c) << 1
    tamanho = 1 << comp_max
    t = [0] * tamanho
    for padrao, L, sym in entradas:
        for alto in range(1 << (comp_max - L)):
            t[padrao | (alto << L)] = (sym << 4) | L
    return t, tamanho - 1


_T_LIT, _M_LIT = _tabela_rapida(_LIT)
_T_LEN, _M_LEN = _tabela_rapida(_LEN)
_T_DIST, _M_DIST = _tabela_rapida(_DIST)


def blast(dados, pos=0):
    data = bytes(dados[pos:])
    n = len(data)
    data += bytes(16)
    if n < 2:
        raise ValueError("dados curtos")
    lit, dic = data[0], data[1]
    if lit > 1 or dic < 4 or dic > 6:
        raise ValueError("cabecalho de compactacao invalido")
    TL, ML, TN, MN, TD, MD = _T_LIT, _M_LIT, _T_LEN, _M_LEN, _T_DIST, _M_DIST
    BASE, EXTRA = _BASE, _EXTRA
    out = bytearray()
    p = 2
    buf = 0
    cnt = 0
    try:
        while True:
            while cnt < 32:
                buf |= data[p] << cnt
                p += 1
                cnt += 8
            flag = buf & 1
            buf >>= 1
            cnt -= 1
            if flag:
                e = TN[buf & MN]
                L = e & 15
                if not L:
                    raise ValueError("codigo invalido")
                buf >>= L
                cnt -= L
                s = e >> 4
                ex = EXTRA[s]
                comp = BASE[s] + (buf & ((1 << ex) - 1))
                buf >>= ex
                cnt -= ex
                if comp == 519:
                    if p - (cnt >> 3) - 1 > n:
                        raise ValueError("fluxo compactado incompleto")
                    break
                sh = 2 if comp == 2 else dic
                while cnt < 32:
                    buf |= data[p] << cnt
                    p += 1
                    cnt += 8
                e = TD[buf & MD]
                L = e & 15
                if not L:
                    raise ValueError("codigo invalido")
                buf >>= L
                cnt -= L
                dist = ((e >> 4) << sh) + (buf & ((1 << sh) - 1)) + 1
                buf >>= sh
                cnt -= sh
                tam = len(out)
                if dist > tam:
                    raise ValueError("distancia invalida")
                ini = tam - dist
                if comp <= dist:
                    out += out[ini:ini + comp]
                else:
                    out += (out[ini:] * (comp // dist + 1))[:comp]
            else:
                if lit:
                    e = TL[buf & ML]
                    L = e & 15
                    if not L:
                        raise ValueError("codigo invalido")
                    buf >>= L
                    cnt -= L
                    out.append(e >> 4)
                else:
                    out.append(buf & 255)
                    buf >>= 8
                    cnt -= 8
    except IndexError:
        raise ValueError("fluxo compactado incompleto")
    return bytes(out)


def dbc_para_dbf(bruto):
    tam_cab = struct.unpack("<H", bruto[8:10])[0]
    return bruto[:tam_cab] + blast(bruto, tam_cab + 4)


# ---------------------------------------------------------------- leitura do DBF
def ler_dbf(dbf):
    n_reg, tam_cab, tam_reg = struct.unpack("<IHH", dbf[4:12])
    campos, p = [], 32
    while dbf[p] != 0x0D:
        nome = dbf[p:p + 11].split(b"\x00")[0].decode("latin-1")
        campos.append((nome, dbf[p + 16]))
        p += 32
    pos, cols = 1, []
    for nome, tam in campos:
        cols.append((nome, pos, pos + tam))
        pos += tam
    return n_reg, tam_cab, tam_reg, cols


def inventariar(dbf):
    n_reg, tam_cab, tam_reg, cols = ler_dbf(dbf)
    cheios = {nome: 0 for nome, _, _ in cols}
    distintos = {nome: set() for nome, _, _ in cols}
    dist_sexo, dist_unid_idade, dist_raca = Counter(), Counter(), Counter()
    n = 0
    for i in range(n_reg):
        ini = tam_cab + i * tam_reg
        reg = dbf[ini:ini + tam_reg]
        if len(reg) < tam_reg or reg[0:1] == b"*":
            continue
        n += 1
        for nome, a, b in cols:
            v = reg[a:b].decode("latin-1").strip()
            if v:
                cheios[nome] += 1
                d = distintos[nome]
                if len(d) < 100000:
                    d.add(v)
            if nome == "SEXO":
                dist_sexo[v or "(branco)"] += 1
            elif nome == "IDADE":
                dist_unid_idade[v[:1] or "(branco)"] += 1
            elif nome == "RACACOR":
                dist_raca[v or "(branco)"] += 1
    return {"n": n, "cols": [c[0] for c in cols], "cheios": cheios,
            "distintos": {k: len(v) for k, v in distintos.items()},
            "sexo": dist_sexo, "unid_idade": dist_unid_idade, "raca": dist_raca}


# ---------------------------------------------------------------- download
def baixar(ano, destino):
    """Baixa DOAC<ano>.dbc por FTP anonimo. Retorna False se o arquivo nao existe."""
    ftp = ftplib.FTP(SERVIDOR, timeout=120)
    try:
        ftp.login()
        ftp.set_pasv(True)
        with open(destino, "wb") as f:
            try:
                ftp.retrbinary("RETR " + CAMINHO.format(ano=ano), f.write)
            except ftplib.error_perm as e:
                if str(e).startswith("550"):
                    return False
                raise
        return True
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


def principal():
    resultados, ausentes = {}, []
    with tempfile.TemporaryDirectory() as tmp:
        for ano in ANOS:
            arq = os.path.join(tmp, "DOAC%d.dbc" % ano)
            print("Ano %d ... " % ano, end="", flush=True)
            try:
                if not baixar(ano, arq):
                    print("nao existe no DATASUS")
                    ausentes.append(ano)
                    continue
                with open(arq, "rb") as f:
                    dbf = dbc_para_dbf(f.read())
                res = inventariar(dbf)
                resultados[ano] = res
                print("%d obitos, %d colunas" % (res["n"], len(res["cols"])))
            except Exception as e:  # segue para o proximo ano
                print("FALHOU (%s)" % e)
                ausentes.append(ano)
            finally:
                if os.path.exists(arq):
                    os.remove(arq)
    if not resultados:
        print("Nenhum ano foi lido. Veja as mensagens acima.")
        return
    gravar(resultados, ausentes)


def gravar(res, ausentes):
    anos = sorted(res)
    todas = []
    for a in anos:
        for c in res[a]["cols"]:
            if c not in todas:
                todas.append(c)

    def pct(a, c):
        r = res[a]
        if c not in r["cheios"] or r["n"] == 0:
            return None
        return 100.0 * r["cheios"][c] / r["n"]

    with open(os.path.join(PASTA, "inventario_sim_ac_colunas.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["coluna"] + ["%d_preenchido_pct" % a for a in anos])
        for c in todas:
            w.writerow([c] + ["" if pct(a, c) is None else "%.1f" % pct(a, c) for a in anos])

    chaves = [c for c in todas if any(t in c for t in
              ("SEXO", "IDADE", "DTOBITO", "DTNASC", "RACACOR", "MUN", "BAI", "CEP", "END", "LOGR", "COMPL", "NUMERO", "TIPOBITO", "CAUSABAS"))]
    L = []
    L.append("# Inventario do SIM do Acre\n")
    L.append("Projeto: Quando o territorio importa (C:\\EXPVIDA). Gerado por inventario_sim_ac.py. "
             "Fonte: arquivos publicos DOAC<ano>.dbc do DATASUS. Somente contagens; nenhum registro individual.\n")
    L.append("## Anos lidos\n")
    L.append("Anos com arquivo: %s.\n" % ", ".join(str(a) for a in anos))
    if ausentes:
        L.append("Anos sem arquivo ou com falha: %s.\n" % ", ".join(str(a) for a in ausentes))
    L.append("## Obitos por ano e numero de colunas\n")
    L.append("| Ano | Obitos | Colunas |\n|---|---|---|")
    for a in anos:
        L.append("| %d | %d | %d |" % (a, res[a]["n"], len(res[a]["cols"])))
    L.append("\n## Preenchimento (%) das colunas que importam para o projeto\n")
    L.append("Branco significa campo vazio no arquivo. Uma coluna que nao existe naquele ano aparece com traco.\n")
    L.append("| Coluna | " + " | ".join(str(a) for a in anos) + " |")
    L.append("|---|" + "---|" * len(anos))
    for c in chaves:
        linha = []
        for a in anos:
            p = pct(a, c)
            linha.append("-" if p is None else "%.0f" % p)
        L.append("| %s | %s |" % (c, " | ".join(linha)))
    L.append("\n## Existe nivel territorial abaixo do municipio?\n")
    ter = [c for c in todas if any(t in c for t in ("BAI", "CEP", "LOGR", "ENDRES", "ENDOCOR"))]
    if ter:
        L.append("Colunas com nome ligado a bairro, CEP ou endereco encontradas: %s. "
                 "Veja o preenchimento na tabela acima e no CSV." % ", ".join(ter))
    else:
        L.append("Nenhuma coluna de bairro, CEP ou endereco foi encontrada nos arquivos publicos do Acre. "
                 "Nestes dados, o menor nivel territorial e o municipio de residencia.")
    L.append("\n## Distribuicao de SEXO e unidade da IDADE (ano mais recente lido)\n")
    u = anos[-1]
    L.append("Ano %d. SEXO (1 masculino, 2 feminino, 0 ou 9 ignorado): %s." % (u, dict(res[u]["sexo"])))
    L.append("Primeiro digito de IDADE (1 hora, 2 dia, 3 mes, 4 ano, 5 cem anos ou mais, 0 minuto): %s." % dict(res[u]["unid_idade"]))
    L.append("\n## Municipios de residencia distintos (CODMUNRES) por ano\n")
    for a in anos:
        L.append("- %d: %s" % (a, res[a]["distintos"].get("CODMUNRES", "coluna ausente")))
    L.append("\n## Lembretes de interpretacao\n")
    L.append("- O arquivo traz obitos, nao expectativa de vida. Para a tabua de vida e preciso dividir por populacao (IBGE/MS).")
    L.append("- Idade media ao morrer nao e expectativa de vida.")
    L.append("- Resultados por territorio sao ecologicos, nao individuais.")
    with open(os.path.join(PASTA, "INVENTARIO_SIM_AC.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\nPronto. Gravei INVENTARIO_SIM_AC.md e inventario_sim_ac_colunas.csv em " + PASTA)


if __name__ == "__main__":
    principal()
