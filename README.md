# Colorado Weed Field Guide

119 plant profiles, three source-identified photographs each, and separately sourced hazards for people, pets, other animals and surrounding vegetation. Native volunteers, xeriscape spreaders and invasive and common weeds have their own sections.

The coverage checklist maps all 82 entries in the reviewed Colorado A/B/C lists to illustrated profiles, including explicit synonym and taxon-scope limits. The catalog has 357 photographs. This is a regulatory baseline plus additional common weeds and native hazards, not the entire Colorado flora.

The site follows the published [Stoagen pattern](https://stoagen.com/pattern/index.md): static HTML articles with complete Markdown mirrors, extra evidence notes for agents, text fallbacks, and visible discovery links. No application server, JavaScript execution, authentication or OpenAI hosting is needed to read the content.

- Website: https://denson.github.io/colorado-weed-field-guide/
- Source: https://github.com/denson/colorado-weed-field-guide
- Agent entry: https://denson.github.io/colorado-weed-field-guide/start.md

## Build and preview

Requires Python 3.12 or later.

```sh
python -m pip install -r requirements.txt
python build.py
python validate.py
```

For local viewing, rebuild with local URLs:

```sh
python build.py --base-url http://localhost:3000
python -m http.server 3000 --directory _site
```

For another static host, pass its full HTTPS base URL to `build.py --base-url`. Upload the contents of `_site`. GitHub Actions builds, validates, and deploys on pushes to `main`; Pages must be configured to use GitHub Actions.

## Content and provenance

- `content/plants/*.md`: canonical plant articles, metadata and agent appendices.
- `content/pages/*.md`: safety, about, and agent documentation.
- `data/coverage.json`: complete state-list baseline, profile mappings and open gaps.
- `data/concerns.json`: editorial routes to high-impact hazards, backed by profile evidence.
- `data/sources.json`: source URLs, locators, dates and retrieval hashes.
- `data/images.json`: image identification, creator, license, source URLs and actual-file hashes.
- `data/exclusions.json`: sources deliberately excluded or limited because of mismatches.
- `data/revisions.json` and `data/change-log.jsonl`: content hashes and actual revision-recording timestamps. These are not source publication dates or expert-review dates.
- `assets/photos/`: credited, openly reusable reference photographs.

After editing content or source data, run `python record_revisions.py`, then rebuild and validate. The validator rejects unrecorded changes. Git history independently records changes to code and authored content. It does not silently update old research dates during a build.

Every HTML page has `index.md` and byte-identical `index.md.txt` forms. The `llms-full.txt` corpus contains each page once. `catalog.json`, `provenance.json`, RSS, sitemap, structured page metadata and a generated-file hash manifest support agents and downstream tools.

## Editorial status and rights

AI-assisted educational synthesis; independent botanical and veterinary expert review is pending. This is not a complete Colorado flora or a clinical identification/diagnosis tool. Unresolved toxicity questions are explicit. No safe dose is inferred from another species, genus or animal group.

Each photo retains its own license, attribution and source link. CC BY-SA requirements apply to adaptations of the relevant photos. The site does not relicense third-party photographs or source publications. No blanket project license is assigned to the owner's newly authored code or prose; rights are reserved unless the owner chooses a license later.

Research-response hashes establish retrieval bytes, not scientific truth. Full copyrighted source publications are not included in the repository. All displayed plant photographs are factual source images; no generative plant images are used.
