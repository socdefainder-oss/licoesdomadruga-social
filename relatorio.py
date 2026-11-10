"""Relatorio de desempenho do @licoesdomadruga (roda no GitHub Actions com os secrets).

Sem instagram_manage_insights: mostra curtidas e comentarios de cada post.
Com instagram_manage_insights: mostra tambem alcance, visualizacoes, salvamentos,
compartilhamentos, visitas ao perfil e seguidores ganhos por post, e os numeros da conta.
O token nunca e impresso. Saida: relatorio.md (e no log).
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

GRAPH = "https://graph.facebook.com/v23.0"
TOKEN = os.environ["IG_TOKEN"]
IG = os.environ["IG_USER_ID"]
BRT = timezone(timedelta(hours=-3))


def get(caminho, **params):
    params["access_token"] = TOKEN
    try:
        with urllib.request.urlopen(f"{GRAPH}/{caminho}?{urllib.parse.urlencode(params)}", timeout=40) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return {"erro": json.load(e).get("error", {}).get("message", str(e))}
        except Exception:
            return {"erro": str(e)}


linhas = []
conta = get(IG, fields="username,followers_count,follows_count,media_count")
agora = datetime.now(BRT).strftime("%d/%m/%Y %H:%M")
linhas.append(f"# Relatorio @{conta.get('username')} — {agora} (Brasilia)\n")
linhas.append(f"Seguidores: **{conta.get('followers_count')}** · seguindo: {conta.get('follows_count')} · posts: {conta.get('media_count')}\n")

# insights da conta (ultimos dias)
tem_insights = True
for metrica in ("reach", "views", "accounts_engaged", "total_interactions", "profile_views", "follows_and_unfollows"):
    r = get(f"{IG}/insights", metric=metrica, period="day", metric_type="total_value",
            since=int((datetime.now(BRT) - timedelta(days=2)).timestamp()), until=int(datetime.now(BRT).timestamp()))
    if "erro" in r:
        if "permission" in r["erro"].lower() or "(#10)" in r["erro"] or "(#200)" in r["erro"]:
            tem_insights = False
            linhas.append(f"\n_Insights da conta indisponiveis: {r['erro'][:160]}_\n")
            break
        linhas.append(f"- conta/{metrica}: n/d ({r['erro'][:90]})")
        continue
    for d in r.get("data", []):
        tv = d.get("total_value", {})
        linhas.append(f"- Conta · {metrica} (48h): **{tv.get('value')}**"
                      + (f" {tv.get('breakdowns')}" if tv.get("breakdowns") else ""))

midias = get(f"{IG}/media", fields="id,timestamp,media_type,media_product_type,like_count,comments_count,permalink,caption", limit=50)
linhas.append("\n| Publicado | Tipo | Tema | Curtidas | Coment. | Alcance | Views | Salvos | Compart. | Visitas perfil | Seguiu |")
linhas.append("|---|---|---|---|---|---|---|---|---|---|---|")
for m in midias.get("data", []):
    quando = datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00")).astimezone(BRT).strftime("%d/%m %H:%M")
    tema = (m.get("caption") or "").split("\n")[0][:45].replace("|", "/")
    vals = {}
    if tem_insights:
        for metrica in ("reach", "views", "saved", "shares", "profile_visits", "follows"):
            r = get(f"{m['id']}/insights", metric=metrica)
            vals[metrica] = r["data"][0]["values"][0]["value"] if r.get("data") else "n/d"
    v = lambda k: vals.get(k, "—")
    linhas.append(f"| {quando} | {m.get('media_type')} | {tema} | {m.get('like_count')} | {m.get('comments_count')} | "
                  f"{v('reach')} | {v('views')} | {v('saved')} | {v('shares')} | {v('profile_visits')} | {v('follows')} |")
if "erro" in midias:
    linhas.append(f"\nErro ao listar posts: {midias['erro']}")

texto = "\n".join(linhas)
print(texto)
open("relatorio.md", "w", encoding="utf-8").write(texto + "\n")
