-- Grilo Falante v3.0 - Seed Data
-- Initial curator and trusted sources

-- Default human curator (system)
INSERT INTO curators (curator_key, name, curator_type, specializations, accountability_score)
VALUES ('system', 'System Curator', 'human', ARRAY['system', 'governance'], 1.0)
ON CONFLICT (curator_key) DO NOTHING;

-- Default LLM curator
INSERT INTO curators (curator_key, name, curator_type, specializations, accountability_score)
VALUES ('llm-default', 'Default LLM Curator', 'llm', ARRAY['reasoning', 'analysis'], 0.7)
ON CONFLICT (curator_key) DO NOTHING;

-- Trusted sources (Tier 1 - auto-curated)
INSERT INTO governed_sources (source_key, title, source_type, source_origin, tier, validation_status, ingestion_origin)
VALUES
    ('arxiv', 'arXiv Preprint Server', 'database', 'arXiv API', 'tier_1', 'approved', 'automatic'),
    ('pubmed', 'PubMed Central', 'database', 'PubMed API', 'tier_1', 'approved', 'automatic'),
    ('openalex', 'OpenAlex', 'database', 'OpenAlex API', 'tier_1', 'approved', 'automatic'),
    ('ieee', 'IEEE Xplore', 'database', 'IEEE API', 'tier_1', 'approved', 'automatic'),
    ('acm', 'ACM Digital Library', 'database', 'ACM API', 'tier_1', 'approved', 'automatic')
ON CONFLICT (source_key) DO NOTHING;

-- Session preferences for default session
INSERT INTO session_preferences (session_id, topics, domains, recency_weight, preferred_categories)
VALUES ('default', ARRAY[], ARRAY[], 0.3, ARRAY['M1', 'M2', 'M5', 'M7'])
ON CONFLICT (session_id) DO NOTHING;
