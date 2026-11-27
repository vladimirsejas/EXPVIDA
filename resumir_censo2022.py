"""
Projeto: EXPVIDA (C:\\EXPVIDA) - encolhe o CENSO2022_SOCIO_MUNICIPIOS.csv (muito grande) num arquivo pequeno.

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva 1 a 3 minutos.
Guarda as variaveis em percentual (%) ou em reais (R$), e as tabelas de faixa de renda e saneamento inteiras, e troca os textos longos por codigos.
Grava:
  CENSO2022_COMPACTO.csv      tabela;cod;municipio;valor
  CENSO2022_DICIONARIO.csv    tabela;cod;variavel;unidade;categoria;nome_tabela
Nao apaga nada. Depois de conferido, o CENSO2022_SOCIO_MUNICIPIOS.csv pode ser apagado por voce para liberar espaco.
"""
import csv
import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
csv.field_size_limit(10 ** 7)

TODAS = {"10296", "6803", "6805", "6892", "6806"}  # guardadas inteiras (contagens), para calcular percentuais
dic = {}
n_in = n_out = 0
with open(os.path.join(PASTA, "CENSO2022_SOCIO_MUNICIPIOS.csv"), encoding="utf-8", newline="") as f, \
        open(os.path.join(PASTA, "CENSO2022_COMPACTO.csv"), "w", encoding="utf-8", newline="") as g:
    r = csv.reader(f, delimiter=";")
    w = csv.writer(g, delimiter=";")
    next(r)
    w.writerow(["tabela", "cod", "municipio", "valor"])
    for tabela, nome, variavel, unidade, categoria, municipio, valor in r:
        n_in += 1
        u = unidade.strip().lower()
        if not (u.startswith("%") or "rea" in u or "percent" in u or tabela in TODAS):
            continue
        if valor in ("-", "...", "X", ""):
            continue
        chave = (tabela, variavel, unidade, categoria)
        cod = dic.get(chave)
        if cod is None:
            cod = dic[chave] = (len(dic) + 1, nome)
        w.writerow([tabela, cod[0], municipio, valor])
        n_out += 1
with open(os.path.join(PASTA, "CENSO2022_DICIONARIO.csv"), "w", encoding="utf-8", newline="") as g:
    w = csv.writer(g, delimiter=";")
    w.writerow(["tabela", "cod", "variavel", "unidade", "categoria", "nome_tabela"])
    for (t, v, u, c), (cod, nome) in sorted(dic.items(), key=lambda x: x[1][0]):
        w.writerow([t, cod, v, u, c, nome])
print("Linhas lidas: %d | guardadas: %d | combinacoes: %d" % (n_in, n_out, len(dic)))
print("\nPronto. Pode fechar.")
