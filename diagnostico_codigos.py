"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
Diagnostico: por que quase todos os obitos de 2000 a 2009 ficaram "fora da lista" de municipios?
Compara o formato dos codigos de municipio (tamanho e exemplos) entre o SIM e a populacao,
em varios anos. Depois roda a busca de tabelas auxiliares. Grava DIAGNOSTICO_CODIGOS.md.
Somente codigos de municipio (nao sao dados individuais) e contagens.
"""
import io
import os
import sys
import zipfile
from collections import Counter

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario_sim_ac as inv
import piloto_expectativa as pil
import procurar_tabelas_auxiliares as aux

PASTA = os.path.dirname(os.path.abspath(__file__))
ANOS = (2000, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010)


def codigos_sim(dbf):
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dbf)
    pos = {nome: (a, b) for nome, a, b in cols}
    a, b = pos["CODMUNRES"]
    c = Counter()
    for i in range(n_reg):
        reg = dbf[tam_cab + i * tam_reg: tam_cab + (i + 1) * tam_reg]
        if len(reg) < tam_reg or reg[0:1] == b"*":
            continue
        c[reg[a:b].decode("latin-1")] += 1
    return c, (b - a)


def codigos_pop(dados):
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dados)
    pos = {nome: (a, b) for nome, a, b in cols}
    a, b = pos["COD_MUN"]
    s = set()
    for i in range(n_reg):
        reg = dados[tam_cab + i * tam_reg: tam_cab + (i + 1) * tam_reg]
        if len(reg) < tam_reg:
            continue
        s.add(reg[a:b].decode("latin-1"))
        if len(s) > 100000:
            break
    return s, (b - a)


def main():
    L = ["# Diagnostico dos codigos de municipio (SIM x populacao), Acre\n",
         "Cada linha: ano; no SIM, largura do campo CODMUNRES, codigos distintos, quantos casam com a populacao "
         "(comparando os 6 primeiros digitos), exemplos de codigos que NAO casam; na populacao, largura de COD_MUN e exemplos.\n"]
    ftp = pil.ftp_conectar()
    for ano in ANOS:
        try:
            print("Ano %d ..." % ano, flush=True)
            bruto = pil.baixar_bytes(ftp, "/dissemin/publicos/SIM/CID10/DORES/DO%s%d.dbc" % (pil.UF, ano))
            sim, lsim = codigos_sim(inv.dbc_para_dbf(bruto))
            zb = pil.baixar_bytes(ftp, "/dissemin/publicos/IBGE/POPSVS/POPSBR%02d.zip" % (ano % 100))
            with zipfile.ZipFile(io.BytesIO(zb)) as z:
                dados = z.read(z.namelist()[0])
            pop, lpop = codigos_pop(dados)
            pop_ac = sorted(c for c in pop if c.startswith("12"))
            pop6 = {c[:6] for c in pop_ac}
            casam = sum(v for k, v in sim.items() if k[:6] in pop6)
            total = sum(sim.values())
            nao = [(k, v) for k, v in sim.items() if k[:6] not in pop6]
            nao.sort(key=lambda kv: -kv[1])
            L.append("- %d: SIM largura %d, %d codigos distintos, casam %d de %d obitos; nao casam (exemplos): %s. "
                     "Populacao: largura %d, %d municipios do Acre, exemplos: %s." % (
                         ano, lsim, len(sim), casam, total,
                         ", ".join("'%s' (%d)" % kv for kv in nao[:6]) or "nenhum",
                         lpop, len(pop_ac), ", ".join("'%s'" % c for c in pop_ac[:4])))
        except Exception as e:
            L.append("- %d: falhou (%s)" % (ano, e))
    try:
        ftp.quit()
    except Exception:
        ftp.close()
    with open(os.path.join(PASTA, "DIAGNOSTICO_CODIGOS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("Diagnostico gravado. Agora as tabelas auxiliares ...")
    aux.main()


if __name__ == "__main__":
    main()
