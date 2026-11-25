"""
Projeto: Quando o territorio importa (EXPVIDA), estudo de divergencia territorial.
O que faz: baixa do DATASUS a tabela CADMUN (a mesma que o EXPVIDA ja usa) e grava um arquivo pequeno,
MUNICIPIO_MICRORREGIAO.csv (codigo do municipio e da microrregiao), na mesma pasta deste script.
Para que: com isso o Claude monta quais microrregioes sao vizinhas e valida o modelo com dependencia espacial.
Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva menos de 1 minuto.
Nao precisa instalar nada, nao altera nenhum arquivo do EXPVIDA e nao cria pastas. Apenas le a CADMUN.
"""
import csv
import ftplib
import io
import os
import struct

SERVIDOR = "ftp.datasus.gov.br"
CAMINHO = "/dissemin/publicos/SIM/CID10/TABELAS/CADMUN.DBF"
PASTA = os.path.dirname(os.path.abspath(__file__))


def baixar():
    ftp = ftplib.FTP(SERVIDOR, timeout=300)
    ftp.login()
    ftp.set_pasv(True)
    buf = io.BytesIO()
    ftp.retrbinary("RETR " + CAMINHO, buf.write)
    try:
        ftp.quit()
    except Exception:
        ftp.close()
    return buf.getvalue()


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


bruto = baixar()
n_reg, tam_cab, tam_reg, cols = ler_dbf(bruto)
pos = {nome: (a, b) for nome, a, b in cols}
campo = lambda reg, nome: reg[pos[nome][0]:pos[nome][1]].decode("latin-1").strip()
linhas = []
for k in range(n_reg):
    reg = bruto[tam_cab + k * tam_reg: tam_cab + (k + 1) * tam_reg]
    if len(reg) < tam_reg or reg[0:1] == b"*":
        continue
    linhas.append([campo(reg, "MUNCOD")[:6], campo(reg, "MUNNOMEX"), campo(reg, "UFCOD"), campo(reg, "MICROCOD")])
destino = os.path.join(PASTA, "MUNICIPIO_MICRORREGIAO.csv")
with open(destino, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["municipio", "nome", "uf", "microrregiao"])
    w.writerows(linhas)
print("Pronto: %d municipios gravados em %s" % (len(linhas), destino))
