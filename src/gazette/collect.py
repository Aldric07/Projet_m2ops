"""Collecte d'une source : lire son flux RSS et écrire ses items en JSON.

On ne garde que ce que la note de cadrage autorise : titre, extrait tronqué, lien,
date, rubriques. Jamais le texte intégral, jamais l'auteur, jamais les images.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import feedparser

USER_AGENT = "LaGazetteBot/0.1 (projet etudiant M2Ops)"
EXCERPT_MAX = 300
TIMEOUT_S = 20

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def clean_text(raw: str) -> str:
    """Retire les balises HTML, décode les entités et normalise les espaces."""
    text = html.unescape(_TAG_RE.sub(" ", raw or ""))
    return _SPACE_RE.sub(" ", text).strip()


def truncate(text: str, limit: int = EXCERPT_MAX) -> str:
    """Coupe le texte à `limit` caractères au plus, sur une fin de mot."""
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.") + "…"


def _published_at(entry: feedparser.FeedParserDict) -> str | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=UTC).isoformat()


def parse_feed(content: bytes, source: str, fetched_at: datetime) -> list[dict]:
    """Transforme un flux RSS/Atom en items, avec uniquement les champs autorisés."""
    feed = feedparser.parse(content)
    if feed.bozo and not feed.entries:
        raise ValueError(f"flux illisible pour {source}: {feed.get('bozo_exception')}")

    items = []
    for entry in feed.entries:
        link = entry.get("link")
        title = clean_text(entry.get("title", ""))
        if not link or not title:
            continue
        items.append(
            {
                "source": source,
                "guid": entry.get("id") or link,
                "title": title,
                # `summary` vient de <description> ; on ignore volontairement
                # `content` (content:encoded, body…) qui peut contenir l'article entier.
                "excerpt": truncate(clean_text(entry.get("summary", ""))),
                "link": link,
                "published_at": _published_at(entry),
                "categories": [t["term"] for t in entry.get("tags", []) if t.get("term")],
                "fetched_at": fetched_at.isoformat(),
            }
        )
    return items


def load_source_url(name: str, sources_csv: Path) -> str:
    """Retrouve l'adresse du flux d'une source dans sources.csv (colonne `acces`)."""
    with sources_csv.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["nom"].strip().casefold() == name.strip().casefold():
                return row["acces"].split()[0]
    raise KeyError(f"source inconnue dans {sources_csv}: {name}")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        return response.read()


def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def write_items(items: list[dict], source: str, out_dir: Path, fetched_at: datetime) -> Path:
    """Écrit le brut dans out_dir/AAAA-MM-JJ/HHMMSS-<source>.json."""
    day_dir = out_dir / fetched_at.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    path = day_dir / f"{fetched_at:%H%M%S}-{slugify(source)}.json"
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collecte une source de sources.csv.")
    parser.add_argument("--source", default="La Croix", help="nom de la source (colonne `nom`)")
    parser.add_argument("--sources-csv", type=Path, default=Path("sources.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/raw"))
    args = parser.parse_args(argv)

    fetched_at = datetime.now(UTC)
    url = load_source_url(args.source, args.sources_csv)
    items = parse_feed(fetch(url), args.source, fetched_at)
    path = write_items(items, args.source, args.out_dir, fetched_at)
    print(json.dumps({"source": args.source, "items": len(items), "path": str(path)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
