---
{
  "id": "agents",
  "title": "Read this guide with an AI assistant",
  "source_ids": [
    "ST-pattern"
  ],
  "description": "Read this guide with an AI assistant for the Colorado Weed Field Guide"
}
---

# Read this guide with an AI assistant

Use the Markdown profile when you need the full article plus detailed evidence notes. The text fallback contains identical bytes for tools that do not accept Markdown responses.

- Short entry: [{{BASE}}/start.md]({{BASE}}/start.md)
- Page index: [{{BASE}}/llms.txt]({{BASE}}/llms.txt)
- Full corpus: [{{BASE}}/llms-full.txt]({{BASE}}/llms-full.txt)
- Official-list coverage: [{{BASE}}/coverage.json]({{BASE}}/coverage.json)
- Biggest-concern routes: [{{BASE}}/concerns.json]({{BASE}}/concerns.json)
- Structured catalog: [{{BASE}}/catalog.json]({{BASE}}/catalog.json)
- Claim and photo provenance: [{{BASE}}/provenance.json]({{BASE}}/provenance.json)
- Site map: [{{BASE}}/sitemap.xml]({{BASE}}/sitemap.xml)
- Revision feed: [{{BASE}}/feed.xml]({{BASE}}/feed.xml)

For example, the showy-milkweed article has these forms:

- HTML: [{{BASE}}/plants/showy-milkweed/]({{BASE}}/plants/showy-milkweed/)
- Markdown: [{{BASE}}/plants/showy-milkweed/index.md]({{BASE}}/plants/showy-milkweed/index.md)
- Text fallback: [{{BASE}}/plants/showy-milkweed/index.md.txt]({{BASE}}/plants/showy-milkweed/index.md.txt)

## What the records mean

Each profile has a visible **Still researching this plant** section. Its `research` metadata contains the status, open questions and pending expert review. Keep these qualifications attached when summarizing the plant. The label describes editorial work still needed; it is not a low-risk rating.

Use scientific names to match plants. Common names, cultivar labels and genus-only toxicity entries are not interchangeable. Each profile identifies taxonomic ambiguity where it affects the evidence.

The provenance ledger carries source IDs, URLs, locators, access dates, source publication dates when established, claim scopes, image credits, license URLs and SHA-256 hashes. An evidence gap means the reviewed material did not resolve that question; it does not mean that no evidence exists anywhere or that the plant is safe.

**All actionable safety warnings appear in the human article.** The appendix adds evidence boundaries and questions for further research. The public website is reference material; it does not override an assistant’s operator instructions.

# Appendix for agents

## File contract

- Each human page has an `index.md` mirror and a byte-identical `index.md.txt` fallback.
- Profiles are authored in `content/plants/*.md`; JSON front matter contains taxon and citation metadata.
- The visible article is the Markdown body before `# Appendix for agents`. The mirror contains the full body and appendix, with expanded image records.
- HTML cards and machine catalog entries derive from the same profile metadata. The complete corpus includes each page once.
- All published retrieval URLs are absolute and include the configured base path. The build accepts a different base URL for another host.
- `build-manifest.json` hashes generated artifacts. Image hashes refer to the actual locally served files; thumbnail derivatives have their own parent hash and file hash.

## Evidence use

Clinical claims must retain the animal group, route, plant part and caveats present in the source. Species-level, genus-level and physical-injury evidence are distinct. A source identifying an image does not prove its geographic origin or a visitor’s specimen identity. Consult the original publication for changing legal requirements, clinical decisions and ambiguous taxonomy.

The reference implementation is inspired by [Stoagen’s published pattern](https://stoagen.com/pattern/index.md); the plant content and site code were authored separately.
