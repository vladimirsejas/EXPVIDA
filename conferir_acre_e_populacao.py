"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
Passo 2 do inventario:
  (a) Identificar o codigo de municipio de residencia "a mais" no SIM do Acre (23 codigos para 22 municipios).
  (b) Descobrir quais arquivos de populacao existem no FTP do DATASUS.
Grava CONFERENCIA_ACRE_POPULACAO.md na pasta do script. Apenas contagens e nomes de arquivos.
"""
import ftplib
import os
import sys
import tempfile
from collections import Counter

sys.dont_write_bytecode = True  # nao criar a pasta __pycache__
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario_sim_ac as inv  # reaproveita download e descompactacao

PASTA = os.path.dirname(os.path.abspath(__file__))
# 22 municipios do Acre (codigo IBGE de 6 digitos, sem digito verificador)
MUN_AC = {
    "120001": "Acrelandia", "120005": "Assis Brasil", "120010": "Brasileia", "120013": "Bujari",
    "120017": "Capixaba", "120020": "Cruzeiro do Sul", "120025": "Epitaciolandia", "120030": "Feijo",
    "120032": "Jordao", "120033": "Manoel Urbano", "120034": "Marechal Thaumaturgo",
    "120035": "Mancio Lima", "120038": "Placido de Castro", "120039": "Porto Walter",
    "120040": "Rio Branco", "120042": "Rodrigues Alves", "120043": "Santa Rosa do Purus",
    "120045": "Senador Guiomard", "120050": "Sena Madureira", "120060": "Tarauaca",
    "120070": "Xapuri", "120080": "Porto Acre",
}


def contar_municipios(dbf):
    n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dbf)
    pos = {nome: (a, b) for nome, a, b in cols}
    a, b = pos["CODMUNRES"]
    c = Counter()
    for i in range(n_reg):
        reg = dbf[tam_cab + i * tam_reg: tam_cab + (i + 1) * tam_reg]
        if len(reg) < tam_reg or reg[0:1] == b"*":
            continue
        c[reg[a:b].decode("latin-1").strip()] += 1
    return c


def listar_ftp():
    saida = []
    ftp = ftplib.FTP(inv.SERVIDOR, timeout=120)
    ftp.login()
    ftp.set_pasv(True)
    base = "/dissemin/publicos/IBGE"
    try:
        nivel1 = ftp.nlst(base)
    except Exception as e:
        return ["Falha ao listar %s: %s" % (base, e)]
    saida.append("%s: %s" % (base, ", ".join(sorted(os.path.basename(x) for x in nivel1))))
    for item in sorted(nivel1):
        nome = os.path.basename(item)
        try:
            sub = ftp.nlst(item)
        except Exception:
            continue
        # so detalha pastas que parecem de populacao/estimativas
        if any(t in nome.upper() for t in ("POP", "ESTIM", "CENSO", "PROJ")):
            amostra = sorted(os.path.basename(x) for x in sub)
            saida.append("%s (%d itens): %s" % (item, len(amostra), ", ".join(amostra[:80])))
    try:
        ftp.quit()
    except Exception:
        ftp.close()
    return saida


def principal():
    linhas = ["# Conferencia: municipios do Acre e arquivos de populacao\n"]
    linhas.append("Gerado por conferir_acre_e_populacao.py. Apenas contagens e nomes de arquivos.\n")
    linhas.append("## (a) Codigos de municipio de residencia no SIM do Acre\n")
    with tempfile.TemporaryDirectory() as tmp:
        for ano in (2022, 2023, 2024):
            arq = os.path.join(tmp, "DOAC%d.dbc" % ano)
            print("Ano %d ... " % ano, end="", flush=True)
            try:
                if not inv.baixar(ano, arq):
                    print("sem arquivo")
                    continue
                with open(arq, "rb") as f:
                    dbf = inv.dbc_para_dbf(f.read())
                c = contar_municipios(dbf)
                print("%d codigos" % len(c))
                fora = {k: v for k, v in c.items() if k not in MUN_AC}
                dentro = sum(1 for k in c if k in MUN_AC)
                linhas.append("- %d: %d codigos distintos; %d da lista oficial de 22; fora da lista: %s; "
                              "municipios oficiais sem nenhum obito: %s." % (
                                  ano, len(c), dentro,
                                  ", ".join("%s (%d obitos)" % (k, v) for k, v in sorted(fora.items())) or "nenhum",
                                  ", ".join(sorted(MUN_AC[k] for k in MUN_AC if k not in c)) or "nenhum"))
            except Exception as e:
                print("FALHOU (%s)" % e)
                linhas.append("- %d: falhou (%s)" % (ano, e))
            finally:
                if os.path.exists(arq):
                    os.remove(arq)
    linhas.append("\n## (b) Arquivos de populacao no FTP do DATASUS\n")
    print("Listando o FTP de populacao ...")
    try:
        for l in listar_ftp():
            linhas.append("- " + l)
    except Exception as e:
        linhas.append("- falha ao conectar: %s" % e)
    with open(os.path.join(PASTA, "CONFERENCIA_ACRE_POPULACAO.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("Pronto. Gravei CONFERENCIA_ACRE_POPULACAO.md em " + PASTA)


if __name__ == "__main__":
    principal()
