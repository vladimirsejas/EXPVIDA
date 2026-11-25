"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
Inspeciona a tabela CADMUN.DBF do DATASUS (cadastro de municipios): quais colunas existem
(nome do municipio, regiao de saude, etc.) e como ficam as linhas do Acre.
Grava CADMUN_ESTRUTURA.md. Tabela de municipios (nao ha dados individuais); baixada para a memoria.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario_sim_ac as inv
import piloto_expectativa as pil

PASTA = os.path.dirname(os.path.abspath(__file__))


def main():
    ftp = pil.ftp_conectar()
    dados = pil.baixar_bytes(ftp, "/dissemin/publicos/SIM/CID10/TABELAS/CADMUN.DBF")
    try:
        ftp.quit()
    except Exception:
        ftp.close()
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dados)
    L = ["# Estrutura da tabela CADMUN.DBF (DATASUS)\n",
         "Registros: %d. Colunas (%d): %s.\n" % (n_reg, len(cols), ", ".join(c[0] for c in cols))]
    linhas = []
    for i in range(n_reg):
        reg = dados[tam_cab + i * tam_reg: tam_cab + (i + 1) * tam_reg]
        if len(reg) < tam_reg or reg[0:1] == b"*":
            continue
        linhas.append({nome: reg[a:b].decode("latin-1").strip() for nome, a, b in cols})
    L.append("Linhas validas: %d.\n" % len(linhas))
    # preenchimento de cada coluna
    L.append("## Preenchimento por coluna\n")
    for nome, _, _ in cols:
        cheios = sum(1 for r in linhas if r[nome])
        dist = len({r[nome] for r in linhas if r[nome]})
        L.append("- %s: %d preenchidos de %d, %d valores distintos." % (nome, cheios, len(linhas), dist))
    # exemplos do Acre
    chave = next((n for n, _, _ in cols if n.upper().startswith("MUNCOD")), cols[0][0])
    ac = [r for r in linhas if r[chave].startswith("12")]
    L.append("\n## Exemplos do Acre (%d linhas)\n" % len(ac))
    for r in ac[:6]:
        L.append("- " + "; ".join("%s=%s" % (k, v) for k, v in r.items() if v))
    with open(os.path.join(PASTA, "CADMUN_ESTRUTURA.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("Pronto. Gravei CADMUN_ESTRUTURA.md em " + PASTA)


if __name__ == "__main__":
    main()
