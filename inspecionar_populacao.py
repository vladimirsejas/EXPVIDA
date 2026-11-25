"""
Projeto: Quando o territorio importa (C:\\EXPVIDA)
Passo 3 do inventario: inspecionar a estrutura do arquivo de populacao do DATASUS
(pasta IBGE/POPSVS), usando o ano de 2022 como amostra, e conferir os dados do Acre.
Grava POPULACAO_ESTRUTURA.md na pasta do script. O arquivo baixado fica em pasta temporaria.
"""
import csv
import ftplib
import io
import os
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict

sys.dont_write_bytecode = True  # nao criar a pasta __pycache__
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario_sim_ac as inv

PASTA = os.path.dirname(os.path.abspath(__file__))
ANO = 22
CAMINHO = "/dissemin/publicos/IBGE/POPSVS/POPSBR%02d.zip" % ANO


def baixar_zip():
    """Baixa o zip para a memoria (nada e gravado em disco)."""
    buf = io.BytesIO()
    ftp = ftplib.FTP(inv.SERVIDOR, timeout=300)
    try:
        ftp.login()
        ftp.set_pasv(True)
        ftp.retrbinary("RETR " + CAMINHO, buf.write)
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    buf.seek(0)
    return buf


def principal():
    L = ["# Estrutura do arquivo de populacao (DATASUS, IBGE/POPSVS, ano 20%02d)\n" % ANO]
    L.append("Gerado por inspecionar_populacao.py. Fonte: %s. Agregados de populacao, sem dados individuais.\n" % CAMINHO)
    if True:
        print("Baixando %s ..." % CAMINHO)
        with zipfile.ZipFile(baixar_zip()) as z:
            L.append("## Conteudo do zip\n")
            for i in z.infolist():
                L.append("- %s (%d bytes)" % (i.filename, i.file_size))
            nome = z.namelist()[0]
            dados = z.read(nome)
        L.append("\n## Arquivo lido: %s\n" % nome)
        baixo = nome.lower()
        if baixo.endswith(".dbf"):
            n_reg, tam_cab, tam_reg, cols = inv.ler_dbf(dados)
            L.append("Formato DBF. Registros: %d. Colunas: %s.\n" % (n_reg, ", ".join(c[0] for c in cols)))
            pos = {c[0]: (c[1], c[2]) for c in cols}
            linhas = []
            for i in range(n_reg):
                reg = dados[tam_cab + i * tam_reg: tam_cab + (i + 1) * tam_reg]
                if len(reg) < tam_reg or reg[0:1] == b"*":
                    continue
                linhas.append({k: reg[a:b].decode("latin-1").strip() for k, (a, b) in pos.items()})
        elif baixo.endswith(".csv") or baixo.endswith(".txt"):
            txt = dados.decode("latin-1")
            amostra = txt[:2000]
            delim = ";" if amostra.count(";") >= amostra.count(",") else ","
            leitor = csv.DictReader(io.StringIO(txt), delimiter=delim)
            linhas = list(leitor)
            L.append("Formato texto (delimitador %r). Registros: %d. Colunas: %s.\n" % (
                delim, len(linhas), ", ".join(leitor.fieldnames or [])))
        else:
            L.append("Formato nao reconhecido pelo script.")
            linhas = []
        if linhas:
            cols = list(linhas[0].keys())
            L.append("## Primeiras 3 linhas (agregados de populacao)\n")
            for r in linhas[:3]:
                L.append("- " + "; ".join("%s=%s" % (k, v) for k, v in r.items()))
            # procura colunas de municipio, sexo e idade
            def acha(*pistas):
                for c in cols:
                    if any(p in c.upper() for p in pistas):
                        return c
                return None
            cmun = acha("COD_MUN", "MUN", "CODMUN")
            csex = acha("SEXO")
            cida = acha("IDADE", "FAIXA", "FXET", "FX_ET")
            cpop = acha("POP", "VALOR")
            L.append("\n## Colunas identificadas\n")
            L.append("Municipio: %s; sexo: %s; idade/faixa: %s; populacao: %s." % (cmun, csex, cida, cpop))
            if cmun:
                ac = [r for r in linhas if str(r[cmun]).startswith("12")]
                L.append("\n## Acre (codigos que comecam por 12)\n")
                L.append("Linhas do Acre: %d. Municipios distintos: %d." % (len(ac), len({r[cmun] for r in ac})))
                if csex:
                    L.append("Valores de sexo no Acre: %s." % dict(Counter(r[csex] for r in ac)))
                if cida:
                    vals = sorted({r[cida] for r in ac})
                    L.append("Valores distintos de idade/faixa no Acre (%d): %s." % (len(vals), ", ".join(vals[:60])))
                if cpop:
                    try:
                        tot = defaultdict(float)
                        for r in ac:
                            tot[r[csex] if csex else "total"] += float(str(r[cpop]).replace(",", "."))
                        L.append("Soma da populacao do Acre por sexo (para conferencia de ordem de grandeza): %s." % {
                            k: int(v) for k, v in tot.items()})
                    except Exception as e:
                        L.append("Nao consegui somar a populacao (%s)." % e)
    with open(os.path.join(PASTA, "POPULACAO_ESTRUTURA.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("Pronto. Gravei POPULACAO_ESTRUTURA.md em " + PASTA)


if __name__ == "__main__":
    principal()
