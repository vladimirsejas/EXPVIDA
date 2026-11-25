"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
Diagnostico: por que o campo SEXO aparece como ignorado em anos antigos no script do Brasil.
Baixa 3 arquivos pequenos do Acre, compara o descompactador novo com o antigo e mostra os bytes de SEXO.
Grava DIAGNOSTICO_SEXO.md.
"""
import io, os, sys, struct
from collections import Counter
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario_sim_ac as inv
import piloto_expectativa as pil

PASTA = os.path.dirname(os.path.abspath(__file__))


def blast_lento(dados, pos):
    b = inv._Bits(dados, pos)
    lit = b.bits(8); dic = b.bits(8)
    saida = bytearray()
    while True:
        if b.bits(1):
            s = b.decode(inv._LEN)
            comp = inv._BASE[s] + b.bits(inv._EXTRA[s])
            if comp == 519:
                break
            sh = 2 if comp == 2 else dic
            dist = (b.decode(inv._DIST) << sh) + b.bits(sh) + 1
            ini = len(saida) - dist
            for i in range(comp):
                saida.append(saida[ini + i])
        else:
            saida.append(b.decode(inv._LIT) if lit else b.bits(8))
    return bytes(saida)


L = ["# Diagnostico do campo SEXO\n"]
ftp = pil.ftp_conectar()
for ano in (2005, 2016, 2019):
    bruto = pil.baixar_bytes(ftp, "/dissemin/publicos/SIM/CID10/DORES/DOAC%d.dbc" % ano)
    tam_cab = struct.unpack("<H", bruto[8:10])[0]
    rapido = bruto[:tam_cab] + inv.blast(bruto, tam_cab + 4)
    lento = bruto[:tam_cab] + blast_lento(bruto, tam_cab + 4)
    L.append("## AC %d\n" % ano)
    L.append("Bytes comprimidos: %d. Descompactado rapido: %d bytes; lento: %d bytes; iguais: %s.\n" % (
        len(bruto), len(rapido), len(lento), rapido == lento))
    for nome, dbf in (("lento", lento),):
        n_reg, tc, tr, cols = inv.ler_dbf(dbf)
        pos = {n: (a, b) for n, a, b in cols}
        s0, s1 = pos["SEXO"]; i0, i1 = pos["IDADE"]; m0, m1 = pos["CODMUNRES"]
        L.append("Registros: %d; tamanho do registro: %d; SEXO nas posicoes %d a %d; IDADE %d a %d; CODMUNRES %d a %d.\n" % (
            n_reg, tr, s0, s1, i0, i1, m0, m1))
        c = Counter(); ci = Counter()
        for k in range(n_reg):
            base = tc + k * tr
            c[dbf[base + s0:base + s1]] += 1
            ci[dbf[base + i0:base + i1]] += 1
        L.append("SEXO (bytes brutos): %s\n" % dict(c.most_common(8)))
        L.append("IDADE (os 8 mais comuns): %s\n" % dict(ci.most_common(8)))
        L.append("Primeiro registro: %r\n" % dbf[tc:tc + tr][:80])
ftp.quit()
with open(os.path.join(PASTA, "DIAGNOSTICO_SEXO.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print("Pronto. Gravei DIAGNOSTICO_SEXO.md em", PASTA)
