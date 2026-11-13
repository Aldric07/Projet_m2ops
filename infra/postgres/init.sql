-- Schéma de la base `gazette` (cf. docs/cadrage.md). Exécuté au premier démarrage de Postgres.
-- Rempli à partir du TD 3 (nettoyage) et du regroupement par thèmes.

CREATE TABLE IF NOT EXISTS articles (
    id           BIGSERIAL PRIMARY KEY,
    source       TEXT        NOT NULL,
    guid         TEXT        NOT NULL,
    title        TEXT        NOT NULL,
    excerpt      TEXT        NOT NULL DEFAULT '' CHECK (char_length(excerpt) <= 300),
    link         TEXT        NOT NULL UNIQUE,
    published_at TIMESTAMPTZ,
    categories   TEXT[]      NOT NULL DEFAULT '{}',
    fetched_at   TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS articles_published_at_idx ON articles (published_at);

CREATE TABLE IF NOT EXISTS editions (
    id           BIGSERIAL PRIMARY KEY,
    edition_date DATE        NOT NULL UNIQUE,
    published_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS themes (
    id          BIGSERIAL PRIMARY KEY,
    edition_id  BIGINT  NOT NULL REFERENCES editions (id) ON DELETE CASCADE,
    label       TEXT    NOT NULL,
    nb_articles INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS article_theme (
    article_id BIGINT NOT NULL REFERENCES articles (id) ON DELETE CASCADE,
    theme_id   BIGINT NOT NULL REFERENCES themes (id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, theme_id)
);
