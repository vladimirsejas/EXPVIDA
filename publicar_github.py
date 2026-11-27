"""
Projeto: EXPVIDA (C:\\EXPVIDA) - envia tudo para o GitHub (vladimirsejas/EXPVIDA), no ramo atual e no ramo main.

Como usar: abra este arquivo no VS Code e clique em "Run Python File". Leva 1 a 5 minutos.
Arquivos com mais de 90 MB nao vao (o GitHub recusa acima de 100 MB): sao colocados no .gitignore
e continuam no notebook. Nada e apagado.
"""
import os
import subprocess

PASTA = os.path.dirname(os.path.abspath(__file__))
LIMITE = 90 * 1024 * 1024


def git(*a):
    r = subprocess.run(["git", *a], cwd=PASTA, capture_output=True, text=True, encoding="utf-8", errors="replace")
    saida = (r.stdout + r.stderr).strip()
    print("> git " + " ".join(a) + ("\n" + saida if saida else ""))
    return r.returncode, saida


# 1) arquivos grandes demais ficam fora
grandes = []
for raiz, dirs, arqs in os.walk(PASTA):
    if ".git" in dirs:
        dirs.remove(".git")
    for n in arqs:
        p = os.path.join(raiz, n)
        if os.path.getsize(p) > LIMITE:
            grandes.append(os.path.relpath(p, PASTA).replace("\\", "/"))
gi = os.path.join(PASTA, ".gitignore")
atual = open(gi, encoding="utf-8").read().splitlines() if os.path.exists(gi) else []
novos = [g for g in grandes if g not in atual]
if novos:
    with open(gi, "a", encoding="utf-8") as f:
        f.write("\n# grandes demais para o GitHub (ficam so no notebook)\n" + "\n".join(novos) + "\n")
for g in grandes:
    git("rm", "--cached", "--ignore-unmatch", "-q", g)
print("Ficam fora do GitHub (grandes demais):", ", ".join(grandes) or "nenhum")

# 2) commit e envio
_, ramo = git("rev-parse", "--abbrev-ref", "HEAD")
git("add", "-A")
cod, _ = git("commit", "-m", "Onda dos homicidios 2000-2024, Censo 2022, CNES e relatorios por municipio\n\n"
             "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n"
             "Claude-Session: https://claude.ai/code/session_01BHsHXwHKV5kuqGTui3hX9Z")
cod, saida = git("push", "-u", "origin", ramo)
if cod == 0 and ramo != "main":
    # leva o mesmo conteudo para o ramo principal (so avanca, nunca apaga nada no GitHub)
    cod, saida = git("push", "origin", "HEAD:main")
    if cod == 0:
        git("fetch", "origin", "main")
if cod == 0:
    git("log", "--oneline", "-3")
    print("\nPronto: tudo enviado para o GitHub, ramos " + ramo + " e main. Pode fechar.")
else:
    print("\nATENCAO: o envio falhou. Copie a mensagem acima para o Claude.")
