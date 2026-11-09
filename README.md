# Publicação automática — @licoesdomadruga

Publica os posts e carrosséis da agenda no Instagram pela API oficial. O GitHub Actions roda de hora em hora (07h–21h de Brasília) e posta o que venceu em `agenda.json`.

- Portfólio Meta: **Seu Madruga** (4004203909753202) · app **Madruga Publicador** (1810441686811580) · usuário do sistema `publicador` (61596050236139) · conta IG 17841424458860624.
- Secrets: `IG_USER_ID`, `IG_TOKEN` (token do usuário do sistema, não expira). Variável: `MEDIA_BASE_URL` = endereço raw da pasta `midia/`.
- Rotina: legenda em `legendas/<id>.txt` (máx. 5 hashtags) → item em `agenda.json` → `python publicar.py preparar` → `python publicar.py publicar --dry-run` → commit e push.
- `origem` dos itens é relativo à pasta `MadrugaEconomista` (ex.: `posts/exemplo_v3/saida/exemplo_v3_01.png`).
