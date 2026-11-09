"""Le o token de novo_token.txt (ignorado pelo git), descobre o IG_USER_ID da conta
@licoesdomadruga e grava os secrets IG_TOKEN e IG_USER_ID no repositorio do GitHub.
O token nunca e impresso. No final o arquivo novo_token.txt e apagado.

Uso: python configurar_token.py            (descobre o ID e grava os secrets)
     python configurar_token.py --so-id    (so descobre e mostra o ID, sem gravar nada)
"""
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ARQ = AQUI / "novo_token.txt"
REPO = "socdefainder-oss/licoesdomadruga-social"
BIZ = "4004203909753202"
CONTA = "licoesdomadruga"
GRAPH = "https://graph.facebook.com/v23.0"

token = ARQ.read_text(encoding="utf-8").strip() if ARQ.exists() else ""
if not token:
    sys.exit(f"Cole o token em {ARQ} (uma linha so) e rode de novo.")


def get(caminho, **params):
    params["access_token"] = token
    url = f"{GRAPH}/{caminho}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"erro": json.load(e).get("error", {}).get("message", str(e))}


eu = get("me", fields="id,name")
print("token pertence a:", eu.get("name"), eu.get("id"), eu.get("erro", ""))
perms = get("me/permissions")
print("permissoes:", [p["permission"] for p in perms.get("data", []) if p.get("status") == "granted"] or perms)

ig_id = None
for borda in ("instagram_business_accounts", "owned_instagram_accounts", "instagram_accounts"):
    r = get(f"{BIZ}/{borda}", fields="id,username")
    contas = r.get("data", [])
    print(f"{borda}:", [(c.get("id"), c.get("username")) for c in contas] or r.get("erro"))
    for c in contas:
        if c.get("username") == CONTA and str(c.get("id", "")).startswith("1784"):
            ig_id = c["id"]
    if ig_id:
        break

if not ig_id:
    sys.exit("Nao achei o ID 1784... da conta. Me mande a saida acima (ela nao contem o token).")

teste = get(ig_id, fields="username,media_count")
print("conta confirmada:", teste)
print("IG_USER_ID =", ig_id)
if "--so-id" in sys.argv:
    sys.exit(0)

for nome, valor in (("IG_USER_ID", ig_id), ("IG_TOKEN", token)):
    subprocess.run(["gh", "secret", "set", nome, "-R", REPO], input=valor.encode(), check=True)
    print("secret gravado:", nome)
ARQ.unlink()
print("novo_token.txt apagado. Pronto.")
