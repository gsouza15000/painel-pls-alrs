#!/usr/bin/env python3
"""Coleta os projetos de lei (PL e PLC) da Assembleia Legislativa do RS.

Lê a pesquisa pública de proposições (ww4.al.rs.gov.br/legislativo/pesquisa), que devolve
a lista completa de um tipo e ano embutida na página. Atualiza docs/data.json, detecta
projetos novos e grava docs/novos.json e docs/meta.json.

Uso:
  python scripts/coletar.py             # só o ano corrente
  python scripts/coletar.py --anos 2023 2024 2025 2026
"""
import argparse, datetime as dt, html, json, os, re, sys, time, urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))
from areas import classificar

BASE = "https://ww4.al.rs.gov.br"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(RAIZ, "docs")
TIPOS = ["PL", "PLC"]
PARTIDOS_CONHECIDOS = {"PT", "PP", "PL", "PSD", "MDB", "PSB", "REPUBLICANOS", "UNIÃO", "PDT", "NOVO",
                       "PODE", "PSOL", "PSDB", "PCDOB", "PC DO B", "PV", "REDE", "CIDADANIA", "AVANTE",
                       "SOLIDARIEDADE", "PRD", "PODEMOS", "DC", "PMB", "AGIR", "MOBILIZA", "PRTB"}
AGORA = dt.datetime.now(ZoneInfo("America/Sao_Paulo"))


def baixar(url, tentativas=4, espera=20):
    ultimo = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "painel-pls-alrs/1.0 (consulta diaria a dados publicos; github.com/gsouza15000/painel-pls-alrs)",
                "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=240) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa
            ultimo = e
            print(f"  tentativa {i+1} falhou: {e}", file=sys.stderr)
            time.sleep(espera * (i + 1))
    raise RuntimeError(f"não foi possível baixar {url}: {ultimo}")


def proposicoes(tipo, ano):
    url = f"{BASE}/legislativo/pesquisa?siglaTipoProposicao={tipo}&anoProposicao={ano}&pagina=1"
    pagina = baixar(url)
    m = re.search(r'<script[^>]*data-drupal-selector="drupal-settings-json"[^>]*>(.*?)</script>', pagina, re.S)
    if not m:
        raise RuntimeError(f"página sem dados embutidos ({tipo} {ano}); o site pode ter mudado")
    cfg = json.loads(html.unescape(m.group(1)) if m.group(1).lstrip().startswith("&") else m.group(1))
    lista = (cfg.get("alergs_opine_proposicoes") or {}).get("proposicoes") or []
    return lista


def partidos_atuais(semente):
    """Tenta atualizar a lista de deputados e partidos; cai na lista salva se a página mudar."""
    try:
        pagina = baixar(f"{BASE}/deputados", tentativas=2, espera=10)
        texto = re.sub(r"<(script|style).*?</\1>", " ", pagina, flags=re.S)
        linhas = html.unescape(re.sub(r"<[^>]+>", "\n", texto)).split("\n")
        linhas = [l.strip() for l in linhas if l.strip()]
        achados = {}
        for a, b in zip(linhas, linhas[1:]):
            if b.upper() in PARTIDOS_CONHECIDOS and a.upper() not in PARTIDOS_CONHECIDOS and 3 <= len(a) <= 40:
                achados[a] = b.upper()
        if len(achados) >= 40:
            print(f"lista de deputados atualizada: {len(achados)}")
            return achados
        print(f"lista de deputados com poucos nomes ({len(achados)}); mantendo a anterior", file=sys.stderr)
    except Exception as e:  # noqa
        print(f"não atualizou deputados: {e}", file=sys.stderr)
    return semente


def converter(p, partidos):
    au = re.sub(r"^Deputado\(a\)\s*", "", (p.get("nomeProponente") or "").strip())
    n = int(p["nroProposicao"]); a = int(p["anoProposicao"]); t = p["siglaTipoProposicao"].strip()
    ementa = (p.get("ementa") or "").strip()
    return {"k": f"{t} {n}/{a}", "t": t, "n": n, "a": a, "au": au,
            "p": partidos.get(au.split(" + ")[0], ""), "o": ementa,
            "s": p.get("descricao") or "", "d": p.get("dthProtocolo") or "",
            "m": p.get("dthSituacaoProposicao") or "", "ar": classificar(ementa)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anos", nargs="*", type=int)
    args = ap.parse_args()
    anos = args.anos or [AGORA.year]

    caminho = os.path.join(DOCS, "data.json")
    antigos = json.load(open(caminho, encoding="utf-8")) if os.path.exists(caminho) else []
    por_chave = {x["k"]: x for x in antigos}
    sem_dados = os.path.join(RAIZ, "scripts", "partidos.json")
    semente = json.load(open(sem_dados, encoding="utf-8"))
    partidos = partidos_atuais(semente)
    if partidos is not semente:
        json.dump(partidos, open(sem_dados, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    novos = []
    for ano in anos:
        for tipo in TIPOS:
            print(f"coletando {tipo} {ano}...")
            lista = proposicoes(tipo, ano)
            ja = sum(1 for x in por_chave.values() if x["t"] == tipo and x["a"] == ano)
            if ja and len(lista) < ja * 0.8:
                raise RuntimeError(f"{tipo} {ano}: o site devolveu {len(lista)} e já temos {ja}; "
                                   "abortando para não perder dados")
            for p in lista:
                item = converter(p, partidos)
                antigo = por_chave.get(item["k"])
                if antigo is None:
                    item["dt"] = AGORA.strftime("%Y-%m-%d")
                    novos.append(item)
                elif antigo.get("dt"):
                    item["dt"] = antigo["dt"]
                por_chave[item["k"]] = item
            print(f"  {len(lista)} proposições")

    # reclassifica e reaplica partidos em tudo (regras e lista de deputados podem ter mudado)
    for x in por_chave.values():
        x["ar"] = classificar(x["o"])
        x["p"] = partidos.get(x["au"].split(" + ")[0], x.get("p", ""))

    todos = sorted(por_chave.values(), key=lambda x: (x["a"], x["n"], x["t"]))
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in todos) + "\n]\n")

    # novos.json: acumula os detectados nos últimos 30 dias
    cam_novos = os.path.join(DOCS, "novos.json")
    anteriores = []
    if os.path.exists(cam_novos):
        anteriores = json.load(open(cam_novos, encoding="utf-8")).get("novos", [])
    corte = (AGORA - dt.timedelta(days=30)).strftime("%Y-%m-%d")
    chaves = {x["k"] for x in novos}
    mantidos = [x for x in anteriores if x["dt"] >= corte and x["k"] not in chaves]
    reg = [{"k": x["k"], "au": x["au"], "p": x["p"], "ar": x["ar"], "o": x["o"], "d": x["d"], "dt": x["dt"],
            "url": f"{BASE}/legislativo/pesquisa?siglaTipoProposicao={x['t']}&nroProposicao={x['n']}&anoProposicao={x['a']}"}
           for x in novos]
    with open(cam_novos, "w", encoding="utf-8") as f:
        json.dump({"gerado_em": AGORA.isoformat(timespec="minutes"), "novos": reg + mantidos}, f, ensure_ascii=False, indent=1)

    with open(os.path.join(DOCS, "meta.json"), "w", encoding="utf-8") as f:
        json.dump({"atualizado_em": AGORA.isoformat(timespec="minutes"), "total": len(todos),
                   "novos_nesta_coleta": len(novos)}, f, ensure_ascii=False)
    print(f"total {len(todos)}; novos {len(novos)}")


if __name__ == "__main__":
    main()
