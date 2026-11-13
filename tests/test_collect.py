import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from gazette.collect import (
    EXCERPT_MAX,
    clean_text,
    load_source_url,
    parse_feed,
    slugify,
    truncate,
    write_items,
)

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).parent.parent
FETCHED_AT = datetime(2026, 11, 13, 6, 30, tzinfo=UTC)
ALLOWED_KEYS = {
    "source",
    "guid",
    "title",
    "excerpt",
    "link",
    "published_at",
    "categories",
    "fetched_at",
}


def parse_fixture(name: str, source: str = "Test") -> list[dict]:
    return parse_feed((FIXTURES / name).read_bytes(), source, FETCHED_AT)


def test_parse_real_feed_la_croix():
    items = parse_fixture("lacroix_site.xml", "La Croix")

    assert len(items) == 3
    for item in items:
        assert set(item) == ALLOWED_KEYS
        assert item["source"] == "La Croix"
        assert item["link"].startswith("https://www.la-croix.com/")
        assert item["published_at"].startswith("2026-11-13")
        assert len(item["excerpt"]) <= EXCERPT_MAX


def test_author_and_images_are_never_kept():
    raw = json.dumps(parse_fixture("lacroix_site.xml"), ensure_ascii=False)

    assert "Célestine" not in raw  # dc:creator
    assert "i.la-croix.com" not in raw  # enclosure (image)


def test_full_text_is_never_kept():
    first = parse_fixture("pieges.xml")[0]

    assert first["excerpt"] == "Un chapeau court."
    assert "INTEGRAL" not in json.dumps(first)


def test_html_is_removed_from_title():
    first = parse_fixture("pieges.xml")[0]

    assert first["title"] == "Article avec texte intégral & auteur"
    assert first["categories"] == ["Politique", "France"]


def test_long_excerpt_is_truncated_and_missing_date_is_none():
    second = parse_fixture("pieges.xml")[1]

    assert len(second["excerpt"]) <= EXCERPT_MAX
    assert second["excerpt"].endswith("…")
    assert second["published_at"] is None
    assert second["guid"] == second["link"]


def test_item_without_link_is_skipped():
    titles = [item["title"] for item in parse_fixture("pieges.xml")]

    assert "Item sans lien : à ignorer" not in titles


def test_unreadable_feed_raises():
    with pytest.raises(ValueError):
        parse_feed(b"ceci n'est pas un flux", "Test", FETCHED_AT)


@pytest.mark.parametrize(
    ("text", "limit", "expected"),
    [
        ("court", 300, "court"),
        ("un deux trois quatre", 12, "un deux…"),
    ],
)
def test_truncate(text, limit, expected):
    assert truncate(text, limit) == expected


def test_clean_text():
    assert clean_text("<p>a&nbsp;&amp;\n  b</p>") == "a & b"


def test_load_source_url_reads_sources_csv():
    url = load_source_url("la croix", ROOT / "sources.csv")

    assert url == "https://www.la-croix.com/feeds/rss/site.xml"


def test_load_unknown_source_raises():
    with pytest.raises(KeyError):
        load_source_url("Inconnu", ROOT / "sources.csv")


def test_write_items(tmp_path):
    path = write_items([{"title": "é"}], "L'Humanité", tmp_path, FETCHED_AT)

    assert path == tmp_path / "2026-11-13" / "063000-l-humanite.json"
    assert json.loads(path.read_text(encoding="utf-8")) == [{"title": "é"}]


def test_slugify():
    assert slugify("Dernières Nouvelles d'Alsace") == "CASSE-EXPRES"
