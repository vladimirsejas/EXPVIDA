"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
Procura no FTP do DATASUS as tabelas auxiliares que o Brasil inteiro vai precisar:
nomes dos municipios (codigo -> nome, UF) e regioes de saude (para agrupar municipios pequenos).
So lista nomes de pastas e arquivos. Grava TABELAS_AUXILIARES.md na pasta do script.
"""
import ftplib
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario_sim_ac as inv

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTAS = [
    "/dissemin/publicos/IBGE/Auxiliar",
    "/dissemin/publicos/SIM/CID10/TABELAS",
    "/dissemin/publicos/SIM/CID10",
    "/dissemin/publicos/SIM",
    "/dissemin/publicos/CNES/200508_/Auxiliar",
    "/dissemin/publicos/SINASC/NOV/TABELAS",
]
PISTAS = ("MUN", "REGSAUD", "REGIAO", "TERRIT", "CADMUN", "DTB", "UF", "MICRO", "MACRO", "REG")


def main():
    L = ["# Tabelas auxiliares no FTP do DATASUS\n", "Gerado por procurar_tabelas_auxiliares.py. Somente nomes de pastas e arquivos.\n"]
    ftp = ftplib.FTP(inv.SERVIDOR, timeout=120)
    ftp.login()
    ftp.set_pasv(True)
    for p in PASTAS:
        try:
            itens = sorted(os.path.basename(x) for x in ftp.nlst(p))
        except Exception as e:
            L.append("## %s\n\nNao listavel (%s).\n" % (p, str(e)[:80]))
            continue
        L.append("## %s (%d itens)\n" % (p, len(itens)))
        achados = [i for i in itens if any(t in i.upper() for t in PISTAS)]
        L.append("Itens com nome ligado a municipio, regiao ou territorio: %s.\n" % (", ".join(achados) or "nenhum"))
        L.append("Todos (ate 120): %s.\n" % ", ".join(itens[:120]))
    try:
        ftp.quit()
    except Exception:
        ftp.close()
    with open(os.path.join(PASTA, "TABELAS_AUXILIARES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("Pronto. Gravei TABELAS_AUXILIARES.md em " + PASTA)


if __name__ == "__main__":
    main()
