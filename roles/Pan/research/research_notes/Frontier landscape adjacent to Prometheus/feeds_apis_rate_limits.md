# Machine-pollable feeds and APIs for frontier AI / ALife / EC research (as of 2026-10-09)

Method note: every endpoint below was either (a) hit live once from this workstation on 2026-10-09 (~10:47-11:30 UTC) with User-Agent `PrometheusFeedProbe/0.1 (research endpoint verification; low volume)`, cited as "live probe 2026-10-09" with the URL itself as source, or (b) taken from the official documentation page cited. Rate-limit numbers marked "observed" come from response headers on that date. Anything not confirmable is marked UNVERIFIED. No email was sent in any `mailto` parameter, so all Crossref/OpenAlex observations are for the anonymous/public tier.

## 1. arXiv: API, RSS/Atom, OAI-PMH, bulk, terms, 2025-2026 changes

### Takeaway
arXiv offers four pollable surfaces: the Atom search API (`export.arxiv.org/api/query`), daily RSS/Atom listing feeds (`rss.arxiv.org`), OAI-PMH, which moved in March 2025 to `https://oaipmh.arxiv.org/oai`, and bulk S3/Kaggle. All the "legacy" APIs share one hard limit: no more than 1 request per 3 seconds over a single connection, counted across every machine you control. Metadata is CC0. E-print content may be stored for personal or research use but not served. I found no 2025-2026 change to API rate limits. The only October 2026 "rate limit" change covers submissions, not access.

### Cited Findings
**Terms of use and limits**
- ToU, quoted: "make no more than one request every three seconds, and limit requests to a single connection at a time." This applies to the "Legacy APIs: OAI-PMH, RSS, and the arXiv API". The limits "apply to all of the machines under your control as a whole", and you "should not attempt to overcome these limits by increasing the number of machines". The page also says "These limits may change in the future." It shows no last-updated date. — [arXiv API Terms of Use](https://info.arxiv.org/help/api/tou.html)
- ToU: you may "Retrieve, store, transform, and share descriptive metadata about arXiv e-prints". Metadata is released under CC0 1.0. You may "Retrieve, store, and use the content of arXiv e-prints for your own personal use, or for research purposes". You may NOT "Store and serve arXiv e-prints (PDFs, source files, or other content) from your servers" unless the copyright holder or the submission license permits it. Do not imply arXiv endorsement. Linking to the abstract page is encouraged. — [arXiv API ToU](https://info.arxiv.org/help/api/tou.html)
- CONFLICT: the bulk-data page suggests custom harvesting from `export.arxiv.org` at "bursts at 4 requests per second with a 1 second sleep, per burst". This contradicts the ToU's 1 request per 3 s. The same page says not to download the full corpus programmatically: use S3 for complete downloads and programmatic access only "to catch up between bucket updates". — [arXiv bulk data](https://info.arxiv.org/help/bulk_data.html) vs [arXiv API ToU](https://info.arxiv.org/help/api/tou.html)

**Search API (Atom)**
- Endpoint: `GET https://export.arxiv.org/api/query?search_query=cat:cs.NE&sortBy=submittedDate&sortOrder=descending&start=0&max_results=2`
  - Live result: HTTP 200, `application/atom+xml`, `opensearch:totalResults`=18441 for cs.NE.
  - The Atom self-link in the response points to `https://arxiv.org/api/query?...`.
  - Response headers carried no rate-limit headers (server: Google Frontend).
  - Source: [live probe 2026-10-09](https://export.arxiv.org/api/query?search_query=cat:cs.NE&sortBy=submittedDate&sortOrder=descending&start=0&max_results=2)
- Paging: results are "limited to 30000 in slices of at most 2000 at a time", and requests above 30,000 return HTTP 400. Recommended delay is 3 s. — [arXiv API User Manual](https://info.arxiv.org/help/api/user-manual.html)
- Query syntax:
  - Field prefixes: `ti`, `au`, `abs`, `co`, `jr`, `cat`, `rn`, `id`, `all`.
  - Operators: `AND`, `OR`, `ANDNOT`, with parentheses as `%28`/`%29` and phrases as `%22`.
  - Date range: `submittedDate:[YYYYMMDDTTTT+TO+YYYYMMDDTTTT]` (GMT).
  - Sorting: `sortBy` = relevance | lastUpdatedDate | submittedDate; `sortOrder` = ascending | descending.
  - `id_list` takes comma-separated IDs; when combined with `search_query` it filters.
  - Atom extension elements: `arxiv:primary_category`, `arxiv:comment`, `arxiv:journal_ref`, `arxiv:doi`, `opensearch:totalResults`.
  - Source: [arXiv API User Manual](https://info.arxiv.org/help/api/user-manual.html)
- Caching guidance: results only change when new articles are added, so "there is no need to call the API more than once in a day for the same query". — [arXiv API User Manual](https://info.arxiv.org/help/api/user-manual.html)

**RSS/Atom listing feeds**
- URL forms:
  - `https://rss.arxiv.org/rss/<cat>` and `https://rss.arxiv.org/atom/<cat>`.
  - Combine categories with `+` (e.g. `rss/cs.ai+q-bio.NC`). Multi-category feeds have a "Limit 2000 results."
  - Feeds "are updated daily at midnight Eastern Standard Time". The format was revamped in January 2024 (blog post dated 2024/01/31).
  - Source: [arXiv RSS help](https://info.arxiv.org/help/rss.html)
- Live probes, 2026-10-09:
  - `https://rss.arxiv.org/rss/cs.NE`: 200, `application/rss+xml`, 13 KB, `lastBuildDate` "Fri, 09 Oct 2026 04:00:23 +0000" (midnight US Eastern daylight time).
  - `https://rss.arxiv.org/atom/cs.NE+cs.AI`: 200, `application/atom+xml`, 1.05 MB. Entry ids look like `oai:arXiv.org:2610.10541v1`, i.e. October-2026 IDs carry the `2610.` prefix.
  - The legacy `https://export.arxiv.org/rss/cs.NE` still returns 200 with identical content.
  - Sources: [rss cs.NE](https://rss.arxiv.org/rss/cs.NE); [atom cs.NE+cs.AI](https://rss.arxiv.org/atom/cs.NE+cs.AI); [legacy rss](https://export.arxiv.org/rss/cs.NE)

**OAI-PMH**
- Base URL: `https://oaipmh.arxiv.org/oai` (OAI-PMH 2.0).
  - Metadata formats: `oai_dc`, `arXiv` (latest version, authors split out), `arXivRaw` (includes version history).
  - Sets follow `group:archive:CATEGORY`.
  - Datestamp = last modification time. New papers are announced "typically around 10:30pm ET Sunday through Thursday".
  - March 2025 changes: the base URL moved from `http://export.arxiv.org/oai2`; the earliest datestamp moved to 2005-09-16; the resumptionToken "expires daily" and no longer reports total items or cursor.
  - Source: [arXiv OAI-PMH help](https://info.arxiv.org/help/oa/index.html)
- Live probes, 2026-10-09:
  - `verb=Identify`: 200, `earliestDatestamp` 2005-09-16.
  - The old `https://export.arxiv.org/oai2?verb=Identify` redirects (Varnish `location:`) to the new base.
  - `verb=ListSets` returned 183 sets, including `cs:cs:NE`, `cs:cs:AI`, `physics:nlin:AO` (adaptation and self-organizing systems, relevant to ALife) and `physics:nlin:CG`.
  - Sources: [Identify](https://oaipmh.arxiv.org/oai?verb=Identify); [ListSets](https://oaipmh.arxiv.org/oai?verb=ListSets)

**Bulk and full text**
- Metadata bulk: OAI-PMH is "the preferred way to bulk-download or keep an up-to-date copy of arXiv metadata". There is also a full machine-readable dataset on Kaggle. Full-text PDFs and sources are on Amazon S3 (details on `bulk_data_s3.html`). Anyone building indexes from full text "must link back to arXiv for downloads". — [arXiv bulk data](https://info.arxiv.org/help/bulk_data.html)
- Native HTML full text: `https://arxiv.org/html/2408.06292` returned 200 `text/html` (LaTeXML, 612 KB). — [live probe](https://arxiv.org/html/2408.06292)
- ar5iv: `https://ar5iv.labs.arxiv.org/html/1905.10985` still returns 200 (nginx, 292 KB). — [live probe](https://ar5iv.labs.arxiv.org/html/1905.10985)

**2025-2026 changes**
- On 2026-10-01 arXiv added a SUBMISSION rate limit: "up to two submissions per calendar month, with a limit of three total active submissions at any given time", across all submitters and categories. The post does not mention the API, OAI-PMH, RSS or bulk access. — [arXiv blog 2026-10-01](https://blog.arxiv.org/2026/10/01/updated-rate-limit-policy/)
- Third-party blogs claiming an October 2026 API-access rate-limit change (e.g. promptzone.com, kunalganglani.com) cite no primary source. I found no official confirmation. — [search results, unverified](https://www.promptzone.com/joaquin_korhonen/arxiv-rate-limit-policy-updated-october-2026-335m)

### Inferences
- For a "poll every few hours" pipeline, the cheapest correct design is:
  1. One RSS/Atom fetch per category set per day, timed after 04:00-05:00 UTC.
  2. OAI-PMH `ListRecords&metadataPrefix=arXivRaw&set=cs:cs:NE&from=<last datestamp>` for authoritative, version-aware incremental harvest.
  3. The search API only for targeted backfills, with a 3-second sleep and a single connection.
- Polling the search API more than once a day per query wastes budget, because the results are static within a day.
- Because resumptionTokens expire daily, a harvest must finish its token chain within the same day. Persist `from` datestamps, not tokens.
- Storing title/abstract/authors/categories in a private PostgreSQL catalog is clearly allowed (CC0). Caching PDFs or HTML for internal research use is allowed under the "personal use, or for research purposes" clause. Serving them to others is not. Per-paper license URIs (OAI-PMH `arXivRaw` carries license) should be stored so redistributable (CC-BY) items can be flagged.
- The RSS-is-"primarily for human reading" note on the bulk page does not prohibit machine use. It signals that RSS is not the canonical harvest channel.

### Gaps
- Explicit numeric enforcement (e.g. whether violators get 403/503 and for how long) is not documented. No rate-limit headers are returned. UNVERIFIED.
- The S3 bucket name, requester-pays cost, and update cadence were not captured (the `bulk_data_s3.html` content was not retrieved). UNVERIFIED.
- Whether `https://arxiv.org/api/query` (seen in the Atom self-link) is a supported alias for `export.arxiv.org/api/query` is undocumented. Use `export.arxiv.org`.

## 2. Hugging Face Hub: models/datasets/spaces, papers APIs, rate limits, terms

### Takeaway
The Hub API is open without a token:
- Model, dataset and space listings with `search`, `filter`, `sort`, `direction`, `limit`, `expand[]` and cursor pagination via the `Link` header.
- `/api/daily_papers`, `/api/papers`, `/api/papers/search`, `/api/papers/{arxivId}` and `/api/trending`.

Rate limits use 5-minute fixed windows:
- Anonymous: 500 API / 3,000 resolver / 100 page requests per IP.
- Free token: 1,000 / 5,000 / 200.
- There is also an undocumented, much smaller "search" bucket (50 per 5 min anonymous) that applies to paper search.

The live OpenAPI spec is at `huggingface.co/.well-known/openapi.json`.

### Cited Findings
**Rate limits**
- Rate-limit tiers "in September '25", all in 5-minute fixed windows:

  | Plan | API | Resolvers | Pages |
  |---|---|---|---|
  | Anonymous (per IP) | 500 | 3,000 | 100 |
  | Free user | 1,000 | 5,000 | 200 |
  | PRO | 2,500 | 12,000 | 400 |
  | Team | 3,000 | 20,000 | 400 |
  | Enterprise | 6,000 | 50,000 | 600 |
  | Enterprise Plus | 10,000 | 100,000 | 1,000 |
  | Academia Hub | 3,000 | 20,000 | 400 |

  Anonymous and free limits are "subject to change". Over-limit requests get a 429. The Hub implements the IETF draft v9 headers `RateLimit` (`"api|pages|resolvers";r=<remaining>;t=<seconds to reset>`) and `RateLimit-Policy` (`"fixed window";"api";q=<quota>;w=<window s>`). `huggingface_hub` ≥1.2.0 auto-waits on 429. — [HF Hub rate limits](https://huggingface.co/docs/hub/rate-limits)
- Observed anonymous buckets, 2026-10-09:
  - `/api/models`, `/api/datasets`, `/api/spaces`, `/api/daily_papers`, `/api/papers/{id}`, `/api/trending`: `RateLimit-Policy: "fixed window";"api";q=500;w=300`.
  - `/api/papers/search`: a separate bucket, `"fixed window";"search";q=50;w=300`, which is not listed on the docs page.
  - HTML/RSS pages (e.g. `/blog/feed.xml`): `"pages";q=100;w=300`.
  - `/.well-known/openapi.json`: `"media";q=10000;w=300`.
  - Sources: [models](https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=2); [papers search](https://huggingface.co/api/papers/search?q=open-endedness); [blog feed](https://huggingface.co/blog/feed.xml)

**API documentation**
- The API docs have moved to an OpenAPI playground. Spec: `https://huggingface.co/.well-known/openapi.json` (also `.md`). — [HF Hub API](https://huggingface.co/docs/hub/api)
- The live spec (1.16 MB, 298 paths) lists:
  - `GET /api/daily_papers` with params `p` (page, default 0), `limit` (max 100, default 50), `date`, `week`, `month`, `submitter`, and `sort` ∈ {`publishedAt` (default), `trending`}.
  - `GET /api/papers` with `cursor` and `limit` (max 100, default 50).
  - `GET /api/papers/search` with `q` and `limit` (max 120).
  - `GET /api/papers/{paperId}`.
  - `GET /api/trending` with `type` ∈ {all, model, space, dataset} and `limit` (max 20, default 10).
  - `GET /api/collections`.
  - The spec does NOT enumerate GET `/api/models|datasets|spaces` (they work live; see below).
  - Source: [openapi.json, live 2026-10-09](https://huggingface.co/.well-known/openapi.json)

**Live listing and papers endpoints (200 OK, 2026-10-09)**
- `GET /api/models?sort=trendingScore&direction=-1&limit=2`
  - Returns objects with `_id, id, likes, trendingScore, private, downloads, tags[], pipeline_tag, library_name, createdAt, modelId`.
  - Tags encode `arxiv:<id>`, `base_model:...`, `license:...`, `dataset:...`.
  - Pagination is via `Link: <...&cursor=...>; rel="next"`.
  - Source: [live](https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=2)
- `GET /api/models?search=evolution&sort=lastModified&direction=-1&limit=1&expand[]=safetensors&expand[]=gguf&expand[]=cardData&expand[]=downloads&expand[]=likes&expand[]=trendingScore&expand[]=lastModified&expand[]=createdAt`
  - Returns only the expanded fields plus `_id`/`id`.
  - `cardData` is the parsed YAML front matter (`base_model`, `license`, `tags`, ...).
  - `gguf` is an object (`total`, `architecture`, `context_length`, `chat_template`, ...).
  - Source: [live](https://huggingface.co/api/models?search=evolution&sort=lastModified&direction=-1&limit=1&expand%5B%5D=safetensors&expand%5B%5D=gguf&expand%5B%5D=cardData&expand%5B%5D=downloads&expand%5B%5D=likes&expand%5B%5D=trendingScore&expand%5B%5D=lastModified&expand%5B%5D=createdAt)
- `GET /api/models?filter=evolutionary-algorithms&limit=1` (tag filter) works, returning e.g. `julien31/Soar-qwen-7b`. — [live](https://huggingface.co/api/models?filter=evolutionary-algorithms&limit=1)
- `GET /api/datasets?sort=trendingScore&direction=-1&limit=1` returns `author, disabled, gated, lastModified, likes, trendingScore, sha, description`. — [live](https://huggingface.co/api/datasets?sort=trendingScore&direction=-1&limit=1)
- `GET /api/spaces?sort=likes&direction=-1&limit=1` returns `id, likes, sdk, tags, createdAt`. — [live](https://huggingface.co/api/spaces?sort=likes&direction=-1&limit=1)
- `GET /api/daily_papers?limit=1` and `?date=2026-10-08`
  - Return `[{paper:{id:<arXiv id>, authors[{name, user?, status}], publishedAt, submittedOnDailyAt, title, ...}, ...}]`.
  - Pagination via `Link: <...&p=1>; rel="next"`.
  - Source: [live](https://huggingface.co/api/daily_papers?limit=1)
- `GET /api/papers/2408.06292` returns the paper object keyed by arXiv ID. `GET /api/papers/search?q=open-endedness` returned 120 KB of results. — [live](https://huggingface.co/api/papers/2408.06292); [live](https://huggingface.co/api/papers/search?q=open-endedness)
- `GET /api/trending?type=model&limit=2` returns `{recentlyTrending:[{repoData:{..., numParameters, availableInferenceProviders}, repoType}]}`. — [live](https://huggingface.co/api/trending?type=model&limit=2)
- HF blog RSS: `https://huggingface.co/blog/feed.xml`. — [live](https://huggingface.co/blog/feed.xml)

**Terms of service**
- The ToS (displayed "Effective Date: September 15, 2022") says users own their content. For public repos, users grant "each User a perpetual, irrevocable, worldwide, royalty-free, non-exclusive license to use, display ...". Changes take effect 10 days after posting. The page does not address scraping, automated access or rate limits. — [HF Terms of Service](https://huggingface.co/terms-of-service)

### Inferences
- Budget: anonymous gives 500 API calls per 5 min, about 144k/day. A few-hourly poll of trending, lastModified and daily papers (with `limit=100` and cursor paging) fits easily without a token. A free token doubles the quota and is recommended by HF ("make sure you always pass a HF_TOKEN"). Paper search is the binding constraint at 50 per 5 min anonymous, so prefer `daily_papers?date=` and `papers?cursor=` over search fan-out.
- Use `expand[]` to keep payloads small and to get `cardData`, `safetensors` (parameter counts by dtype) and `gguf` in a single listing call, instead of per-repo `/api/models/{id}` calls.
- Implement 429 handling by parsing `t=` from the `RateLimit` header, not by fixed backoff.
- Model cards are user content under each repo's license (`cardData.license`). Storing card metadata and text internally is consistent with the public-repo license grant to "each User". Treat card bodies as copyrighted text, and record `license` per row.

### Gaps
- The full list of allowed `expand[]` values for models/datasets/spaces is not in the OpenAPI spec as parsed. Only the values tested live above are confirmed.
- The "search" bucket quota for token holders is UNVERIFIED (only anonymous q=50/300s was observed).
- No dedicated HF ToS clause on API/automated access was found. Whether a separate "Content Policy" or "Acceptable Use" page restricts bulk metadata mirroring is UNVERIFIED.

## 3. Scholarly graph and metadata APIs: Semantic Scholar, OpenAlex, Crossref, OpenReview, DBLP, Papers with Code, alphaXiv, ar5iv, Connected Papers

### Takeaway
Status by service:
- **Semantic Scholar:**
  - Its unauthenticated shared pool is effectively unusable for a pipeline: 3 of 4 anonymous calls got 429 on 2026-10-09.
  - A free key gives 1 RPS.
  - Its license is non-commercial and requires attribution.
- **OpenAlex** (data CC0) moved in 2026 to a metered USD budget:
  - Keyless: $0.10/day ≈ 1,000 "credits".
  - Free key: 10x that.
  - Singleton lookups free, list/filter calls $0.0001, search $0.001.
  - Cap of 100 req/s.
- **Crossref** tightened public-pool list queries to 1 req/s (polite pool: 3 req/s with `mailto`).
- **OpenReview** API v2 now returns `403 ChallengeRequiredError` for anonymous `/notes` queries. `/groups` still works.
- **DBLP**'s search API now sits behind an Anubis proof-of-work bot wall for scripted clients.
- **Papers with Code** is dead (redirects to HF Trending Papers).

### Cited Findings
**Semantic Scholar**
- Rate limits: unauthenticated requests are "rate-limited to 1000 requests per second shared among all unauthenticated users" and "may also be further throttled during periods of heavy use". "The introductory rate limit for an API key is 1 RPS on all endpoints." Include the key with every request. — [S2 API product page](https://www.semanticscholar.org/product/api)
- Observed 2026-10-09 (anonymous):
  - `GET /graph/v1/paper/search?...` returned 429 `{"message":"Too Many Requests. Please wait and try again or apply for a key ..."}`.
  - `GET /graph/v1/paper/arXiv:2408.06292?...` returned 429 twice, several minutes apart.
  - `GET /graph/v1/paper/search/bulk?query="quality diversity"&fields=title,year&sort=publicationDate:desc` returned 200 `{total:1228, token:"...", data:[{paperId,title,year}]}`.
  - No rate-limit headers were returned.
  - Sources: [search](https://api.semanticscholar.org/graph/v1/paper/search?query=open-endedness&limit=2&fields=title,year,externalIds,publicationDate); [bulk](https://api.semanticscholar.org/graph/v1/paper/search/bulk?query=%22quality%20diversity%22&fields=title,year&sort=publicationDate:desc)
- Endpoint limits, from the live swagger:
  - `/paper/search/bulk` returns "Up to 1,000 papers ... in each call" with a continuation `token`. "Up to 10,000,000 papers can be fetched via this method", beyond which you should use the Datasets API. Nested citations/references are not available through it.
  - `POST /paper/batch` "Can only process 500 paper ids at a time" (`fields` goes in the query string).
  - `/paper/{id}` returns at most 10 MB.
  - `/snippet/search` max limit is 1000.
  - `/paper/search/match` does title match.
  - Source: [S2 Graph API swagger](https://api.semanticscholar.org/graph/v1/swagger.json)
- Datasets API:
  - `GET https://api.semanticscholar.org/datasets/v1/release/` lists weekly-ish release dates. `.../release/latest` returned `release_id` "2026-09-29".
  - Datasets: abstracts (100M records, 30 x 1.8 GB), authors, citations, embeddings-specter_v1/v2 (120M, 30 x 28 GB), paper-ids, papers (200M, 30 x 1.5 GB), publication-venues, s2orc, s2orc_v2 (16M full-text records), tldrs (58M).
  - The README states: "Downloading the full data requires an API key".
  - `.../release/latest/dataset/abstracts` returns 401 `{"error":"A valid API key is required"}`.
  - Sources: [live release list](https://api.semanticscholar.org/datasets/v1/release/); [live latest](https://api.semanticscholar.org/datasets/v1/release/latest)
- License:
  - Use is limited to "internal use solely for the purpose of training and evaluating machine learning models" or "legitimate, non-commercial, research and/or educational purposes". Commercial use needs an expanded license.
  - You may not "repackage or resell" or "sell, lease, share, transfer, sublicense, commercialize" Data.
  - "any public use of Data must point back to Semantic Scholar" and must show the S2 name and logo.
  - Data comes "from copyrighted sources"; the licensee is responsible for copyright compliance.
  - AI2 may throttle "significantly excessive" use and may amend the agreement with 30 days' notice. No version date is shown.
  - Source: [S2 API License Agreement](https://api.semanticscholar.org/license/)

**OpenAlex**
- The help page, "Last updated August 19, 2026", says:
  - "you can make basic queries with no key at all"; a free key "raises your daily budget 10x".
  - Pass the key as `api_key=` query param or `Authorization: Bearer`.
  - Cap: 100 requests/second. Exceeding it, or the daily budget, gives 429.
  - Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Credits-Used`, `X-RateLimit-Reset` (seconds until midnight UTC).
  - Source: [OpenAlex rate limits & authentication](https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication)
- Paging and license: `per-page` default 25, max 100. Data is CC0. The JSON `meta.cost_usd` reports per-call cost. — [OpenAlex API reference](https://help.openalex.org/api-reference/authentication.md)
- Observed per-call costs and budget, 2026-10-09, no key:

  | Call | Example | Cost (USD) | Credits |
  |---|---|---|---|
  | Root | `/` | 0.0001 | 1 |
  | List + filter | `works?filter=publication_year:2026,primary_topic.field.id:17&per-page=1` | 0.0001 | 1 |
  | Singleton | `works/W4322419504` | 0 (free) | 0 |
  | Search | `works?search=...` (rewritten to `fulltext.search`) | 0.001 | 10 |
  | Title search | `filter=title.search:...` | 0.001 | 10 |

  The budget headers read `X-RateLimit-Limit-USD: 0.1` and `X-RateLimit-Limit: 1000` (credits). Other exposed headers include `X-RateLimit-Remaining-USD`, `X-RateLimit-Prepaid-Remaining-USD`, `X-RateLimit-Onetime-Remaining`, `X-RateLimit-Cost-Required-USD` and `Retry-After`. — [live works search](https://api.openalex.org/works?search=open-endedness&per-page=2&select=id,doi,title,publication_date); [live root](https://api.openalex.org/)
- CONFLICT: secondary sources (a CASRAI news piece and a search summary of "official docs") say an API key became REQUIRED in 2026 and quote "$1 of free usage every day" with a key and $0.10/day without. The official help page (2026-08-19) says no key is required for basic queries, and the live keyless budget is $0.10/day. The figures agree; the "required" claim does not. — [CASRAI: OpenAlex API keys mandatory](https://casrai.org/news/openalex-api-keys-mandatory-usage-based-pricing-2026) vs [OpenAlex help](https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication)
- `developers.openalex.org` and `docs.openalex.org` now 301-redirect to `help.openalex.org`. `openalex.org/pricing` is JS-rendered and not machine-readable via fetch. — [developers.openalex.org](https://developers.openalex.org/); [openalex.org/pricing](https://openalex.org/pricing)

**Crossref**
- Crossref announced revised REST API limits from 1 December 2025: the limits had been unchanged since 2013 and volume had tripled in five years. — [Crossref blog: Announcing changes to REST API rate limits](https://crossref.org/blog/announcing-changes-to-rest-api-rate-limits/) (numbers via search summary)
- Refinement post dated 21 July 2026:
  - Single-record requests stay at "5 requests per second for the public pool" and "10 requests per second for the polite pool".
  - List queries are limited to "1 request per second for the public pool" and "3 requests per second for the polite pool".
  - Headers: `x-rate-limit-limit`, `x-rate-limit-interval`, and the new `x-rate-limit-type`. 429 means "take a pause".
  - The polite pool is selected by `mailto`. Limits are applied "by email address", shared defaults like info@example.com are throttled together, and "Repeated use of invalid email addresses could lead to your API access being blocked".
  - Source: [Crossref community: Refining REST API limits](https://community.crossref.org/t/refining-rest-api-limits-for-improved-stability-and-reliability/16137)
- Concurrency: the original announcement reportedly set concurrency to 1 (public) and 3 (polite). — [Crossref blog](https://crossref.org/blog/announcing-changes-to-rest-api-rate-limits/) (via search summary; not re-read verbatim)
- Observed 2026-10-09, public pool: `GET /works?query.bibliographic=...&rows=2&select=DOI,title,created` returned headers `x-rate-limit-limit: 1`, `x-rate-limit-interval: 1s`, `x-api-pool: public-array`. — [live](https://api.crossref.org/works?query.bibliographic=genetic+programming&rows=2&select=DOI,title,created)
- Polite-pool access requires your email in `mailto` or in the User-Agent. Metadata Plus is the paid tier with higher limits. — [Crossref access & authentication](https://crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/) (via search summary)

**OpenReview**
- `GET https://api2.openreview.net/groups?id=ICLR.cc/2026/Conference` returned 200, as did the same call for `ICLR.cc/2027/Conference` and `NeurIPS.cc/2026/Conference`.
  - The group content exposes the invitation and venue ids: `submission_id` = `<venue>/-/Submission`, `submission_venue_id` = `<venue>/Submission`, plus `withdrawn_venue_id`, `desk_rejected_venue_id`, `rejected_venue_id`, and the flag `public_submissions` (true for ICLR 2026 and 2027, false for NeurIPS 2026).
  - Rate-limit headers: `ratelimit-policy: 20;w=60` on `/groups`.
  - Sources: [live ICLR 2026 group](https://api2.openreview.net/groups?id=ICLR.cc/2026/Conference); [live NeurIPS 2026 group](https://api2.openreview.net/groups?id=NeurIPS.cc/2026/Conference); [live ICLR 2027 group](https://api2.openreview.net/groups?id=ICLR.cc/2027/Conference)
- Anonymous `/notes` queries all returned HTTP 403 `{"name":"ChallengeRequiredError","message":"Challenge verification required","details":{"challengeUrl":"https://openreview.net/challenge?redirect=..."}}`, with headers `ratelimit-policy: 180;w=60`.
  - Affected queries: `GET /notes?invitation=ICLR.cc/2026/Conference/-/Submission`, `GET /notes?content.venueid=ICLR.cc/2026/Conference`, and the API v1 `api.openreview.net/notes?invitation=ICLR.cc/2023/Conference/-/Blind_Submission`.
  - The same happened with UA `python-requests/2.32.3` and with no UA.
  - Source: [live notes query](https://api2.openreview.net/notes?content.venueid=ICLR.cc/2026/Conference&limit=1)
- I found no documentation of this challenge mechanism. Context: an OpenReview API vulnerability in November 2025 exposed anonymous-review data around ICLR 2026 and was patched within about an hour. Tightened access is a plausible but UNCONFIRMED cause. — [CASRAI: ICLR 2026 OpenReview breach](https://casrai.org/news/iclr-2026-openreview-breach-reviewer-bribery)
- The openreview-py client logs in with email/password or a token (default token expiry one day, max one week). Newer client source includes MFA handling (`MfaRequiredException` in non-interactive sessions). — [openreview-py client source](https://openreview-py.readthedocs.io/en/latest/_modules/openreview/api/client.html)

**DBLP**
- `GET https://dblp.org/search/publ/api?q=quality%20diversity&format=json&h=2` returned HTTP 200 with `text/html` "Making sure you're not a bot!" (assets under `/.within.website/x/xess/`, the Anubis proof-of-work challenge) instead of JSON. The same happened for a `toc:db/conf/gecco/gecco2025.bht:` query and for the UA `python-requests/2.32.3`. Subsequent requests (no UA, `/xml/`, `/xml/release/`) got TCP connection resets. — [live probe](https://dblp.org/search/publ/api?q=quality%20diversity&format=json&h=2)
- I found no official dblp statement on API bot protection. Third-party guides still describe the API as open, with no key and no published limits. — [search results](https://www.skills.sh/wentorai/research-plugins/dblp-api)

**Papers with Code**
- Live: `https://paperswithcode.com/` and `https://paperswithcode.com/api/v1/papers/?q=evolution` both redirect (CloudFront `Location`) to `https://huggingface.co/papers/trending`, so the old REST API is gone. — [live](https://paperswithcode.com/api/v1/papers/?q=evolution)
- Meta sunset PwC on about 24-25 July 2025. Hugging Face announced the replacement, and the last data snapshot is in the `paperswithcode/paperswithcode-data` JSON dumps. These are secondary sources; I found no official Meta statement. — [hyper.ai](https://hyper.ai/en/news/42900); [Codesota (competitor)](https://www.codesota.com/papers-with-code)

**alphaXiv, ar5iv, Connected Papers**
- alphaXiv:
  - `www.alphaxiv.org` returns 200 HTML (Cloudflare).
  - `https://api.alphaxiv.org/mcp/v1` returned 401 `application/json`: it exists but needs auth.
  - Third-party packages reference API keys created in alphaXiv's MCP/API settings and a dev OpenAPI at `api-dev.alphaxiv.org/api.json`. There is no official public REST reference. UNVERIFIED.
  - Sources: [live alphaxiv.org](https://www.alphaxiv.org/); [axiv PyPI](https://pypi.org/project/axiv/); [agentman alphaXiv MCP listing](https://agentman.ai/agentskills/connections/mcp-server/alphaxiv)
- ar5iv remains live (see section 1). arXiv's native HTML (`arxiv.org/html/<id>`) is the primary HTML full-text route. — [live](https://ar5iv.labs.arxiv.org/html/1905.10985)
- Connected Papers: only the HTML homepage was confirmed (200). I did not check for a public API. — [live](https://www.connectedpapers.com/)

### Inferences
- **Semantic Scholar:** get a key and pace at ≤1 req/s. Use `/paper/search/bulk` with `token` continuation and `POST /paper/batch` (≤500 IDs) for enrichment, such as citation counts, TLDRs and openAccessPdf for arXiv IDs already captured from arXiv/HF. Do not depend on the anonymous pool. The license allows internal non-commercial research use with attribution, which fits a private catalog, but rows must not be redistributed.
- **OpenAlex:** with a free key ($1/day), a few-hourly poll can afford about 10,000 list calls/day, or about 1,000 searches/day. Singleton DOI/ID lookups are free, so resolve by ID instead of searching. Read `X-RateLimit-Remaining-USD` every call and stop at a safety margin.
- **Crossref:** always send `mailto=` (a real, monitored address) to get 3 list req/s. Keep one in-flight request per host. Use `select=` and cursor deep paging (`cursor=*`) for venue sweeps.
- **OpenReview:** plan for authenticated access (an account plus `openreview-py` token) for note harvesting, and verify whether a logged-in token bypasses `ChallengeRequiredError` before committing. Use `/groups` (anonymous, 20/min) to discover venue and invitation IDs. Treat 2FA/MFA on the account as an operational risk for unattended runs.
- **DBLP:** treat the live search API as unavailable to unattended scripts. Prefer the monthly XML dump, which needs verifying, or get DBLP-equivalent venue coverage via Crossref/OpenAlex.
- **Papers with Code:** replace PwC code-links with HF paper pages (`/api/papers/{arxivId}`; whether it exposes GitHub repo links is UNVERIFIED) plus GitHub search on the arXiv ID.

### Gaps
- Whether authenticated OpenReview tokens avoid the challenge, and the OpenReview documented rate limits, are UNVERIFIED (headers show 180/min notes and 20/min groups).
- DBLP dump URLs (`dblp.org/xml/dblp.xml.gz`, Dagstuhl monthly snapshots) could not be reached (connection reset). UNVERIFIED.
- OpenAlex paid-plan prices and the per-call price of content (PDF/XML) downloads are not on a machine-readable official page. The secondary figure of $0.01 per content download is UNVERIFIED. The OpenAlex snapshot (S3) location and cadence were not checked.
- Crossref per-pool concurrency and the Metadata Plus limits as of October 2026 are not stated in the July 2026 post.
- Semantic Scholar per-dataset licenses (e.g. ODC-BY vs restricted abstracts) cannot be read without a key: the dataset detail endpoint returned 401.

## 4. GitHub: REST search, rate limits, trending, releases Atom

### Takeaway
Use these REST endpoints:
- `GET /search/repositories` (q with `topic:`, `pushed:`, `created:`, `stars:` qualifiers; sort stars | forks | help-wanted-issues | updated).
- `GET /search/topics`.

Rate limits:
- Search: 10 requests/min unauthenticated, 30/min with a token.
- Every search is capped at 1,000 results.
- Core: 60/h unauthenticated vs 5,000/h with a PAT.
- GraphQL is unavailable without auth (limit 0).

Other feeds:
- Per-repo releases Atom feeds (`/<owner>/<repo>/releases.atom`) need no API quota.
- There is no official trending API. Only the `github.com/trending` HTML page exists.

### Cited Findings
- Search docs:
  - Authenticated: 30 req/min for all search endpoints except code search, which needs auth and allows 10/min. Unauthenticated: 10 req/min.
  - Up to 1,000 results per search. `per_page` max 100 (default 30).
  - Queries: max 256 characters excluding qualifiers, at most 5 AND/OR/NOT operators.
  - Timeouts set `incomplete_results: true`.
  - `/search/repositories` sort ∈ {stars, forks, help-wanted-issues, updated}, order desc|asc. `/search/topics` has no sort.
  - API version header `X-GitHub-Api-Version: 2026-03-10`.
  - Source: [GitHub REST search docs](https://docs.github.com/en/rest/search/search)
- Primary rate limits:
  - 60/h unauthenticated, per IP.
  - 5,000/h for a PAT.
  - GitHub App installations: 5,000 baseline, scaling to 12,500 (15,000 on Enterprise Cloud).
  - `GITHUB_TOKEN`: 1,000/h per repo.
- Secondary rate limits: ≤100 concurrent requests, ≤900 points/min for REST (GET = 1 point), ≤90 s CPU per 60 s.
- On 403/429 with `x-ratelimit-remaining: 0`, wait until `x-ratelimit-reset`. Honor `retry-after`, otherwise wait at least 1 minute and back off exponentially. "Continuing to make requests while you are rate limited may result in the banning of your integration." — [GitHub REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- Observed 2026-10-09, unauthenticated:
  - `GET /search/repositories?q=topic:open-endedness&sort=updated&order=desc&per_page=1` returned 200 with `total_count` 19, `X-RateLimit-Resource: search`, `X-RateLimit-Limit: 10`, and a `Link` header for next/last.
  - `GET /rate_limit` reported `core` 60, `search` 10, `code_search` 60, `graphql` limit 0.
  - `GET /search/topics?q=evolutionary-algorithms` returned 200 with `total_count` 8.
  - Sources: [live search](https://api.github.com/search/repositories?q=topic:open-endedness&sort=updated&order=desc&per_page=1); [live rate_limit](https://api.github.com/rate_limit); [live topics](https://api.github.com/search/topics?q=evolutionary-algorithms&per_page=1)
- Releases Atom: `https://github.com/SakanaAI/AI-Scientist/releases.atom` returned 200 `application/atom+xml`. — [live](https://github.com/SakanaAI/AI-Scientist/releases.atom)
- Trending: `https://github.com/trending?since=daily` returned 200 HTML (565 KB). There is no JSON. — [live](https://github.com/trending?since=daily)

### Inferences
- With one PAT (30 search/min, 5,000 core/h), a few-hourly sweep of about 20-50 topic/keyword queries (e.g. `topic:open-endedness`, `topic:evolutionary-algorithms`, `topic:artificial-life`, `topic:quality-diversity`, `"arxiv.org/abs/2610" in:readme`) sorted by `updated` with `pushed:>=<last run>` is comfortably within budget. Slice by date qualifiers to stay under the 1,000-result cap.
- Releases Atom feeds and conditional GETs (ETag/If-Modified-Since) are the cheapest way to track a curated list of key repos, because Atom fetches are not counted against API quotas. That last point is inferred and not documented.
- "Trending" should be computed internally as star-velocity deltas from successive `/repos/{owner}/{repo}` snapshots, rather than by scraping the HTML.

### Gaps
- Whether conditional requests returning 304 are exempt from the REST primary limit is not stated on the fetched page.
- GitHub's acceptable-use stance on scraping `/trending` HTML was not checked.

## 5. Conference proceedings feeds: GECCO (ACM DL), ALIFE (MIT Press), NeurIPS/ICLR/ICML (OpenReview)

### Takeaway
Both publisher platforms block scripted access:
- ACM Digital Library (GECCO) returns a Cloudflare challenge (HTTP 403, `cf-mitigated: challenge`).
- MIT Press Direct (ALIFE proceedings, *Artificial Life* journal) does the same.

The pollable path for these venues is Crossref, with OpenAlex as a secondary source. ML conferences are discoverable through OpenReview `/groups`, but note harvesting now needs to clear OpenReview's challenge (see section 3).

### Cited Findings
- `https://dl.acm.org/conference/gecco` returned 403 `cf-mitigated: challenge` ("Just a moment..."). — [live probe](https://dl.acm.org/conference/gecco)
- `https://direct.mit.edu/isal` (ALIFE proceedings) and `https://direct.mit.edu/artl` (journal) both returned 403 `cf-mitigated: challenge`. — [live isal](https://direct.mit.edu/isal); [live artl](https://direct.mit.edu/artl)
- Crossref for MIT Press: `GET /works?filter=prefix:10.1162,from-pub-date:2026-01-01&query.container-title=Artificial+Life&rows=2&select=DOI,title,container-title,published` returned 200 with `total-results` 150 and *Artificial Life* journal items, e.g. DOI `10.1162/artl.a.488` dated 2026-09-21. — [live](https://api.crossref.org/works?filter=prefix:10.1162,from-pub-date:2026-01-01&query.container-title=Artificial+Life&rows=2&select=DOI,title,container-title,published)
- Crossref fuzzy-matches GECCO wrongly: `query.container-title=GECCO` with `from-pub-date:2026-07-01` returned 0 results, and `query.container-title=Genetic+and+Evolutionary+Computation+Conference` matched Springer's "Genetic and Evolutionary Computation" book series (291,125 results), not GECCO proceedings. Precise venue filtering, e.g. by ACM prefix `10.1145` plus the exact proceedings title or ISBN, is needed. — [live](https://api.crossref.org/works?query.container-title=Genetic+and+Evolutionary+Computation+Conference&filter=from-pub-date:2026-01-01&rows=2&select=DOI,title,container-title,published)
- ML venue IDs confirmed via OpenReview `/groups`: `ICLR.cc/2026/Conference`, `ICLR.cc/2027/Conference`, `NeurIPS.cc/2026/Conference`. Group content gives the submission invitation `<venue>/-/Submission` and `venueid` values for accepted, rejected and withdrawn papers. — [live ICLR 2026](https://api2.openreview.net/groups?id=ICLR.cc/2026/Conference)
- ISAL (International Society for Artificial Life) has a WordPress RSS feed at `https://alife.org/feed/` (200, `application/rss+xml`), which carries society news and announcements. — [live](https://alife.org/feed/)
- The OAI-PMH set `physics:nlin:AO` (adaptation and self-organizing systems) and `cs:cs:NE` exist for ALife/EC preprints. — [live ListSets](https://oaipmh.arxiv.org/oai?verb=ListSets)

### Inferences
- For GECCO and ALIFE, the robust pipeline is:
  1. arXiv cs.NE, nlin.AO and cs.AI feeds for preprints.
  2. Crossref (polite pool) daily or weekly sweeps by DOI prefix plus exact container title/ISBN for camera-ready versions.
  3. OpenAlex singleton lookups (free) to enrich DOIs.
- Do not scrape the ACM DL or MIT Press Direct HTML pages: they are Cloudflare-gated, and attempting to bypass the gate would violate their intent.
- ICML venue IDs follow the same `ICML.cc/<year>/Conference` pattern. This is inferred and was not probed.

### Gaps
- The exact Crossref `container-title` strings and ISBNs for GECCO 2026 (ACM) and ALIFE 2026 (MIT Press `isal` DOIs, e.g. `10.1162/isal_a_*`) were not resolved. UNVERIFIED.
- ACM DL eTOC RSS URLs exist historically but could not be reached (Cloudflare). UNVERIFIED.
- The ICML 2026 OpenReview group ID was not probed. Whether NeurIPS 2026 accepted papers become public (`public_submissions: false` at probe time) is unknown.

## 6. Lab blogs and newsletters with RSS

### Takeaway
Confirmed feeds:
- Live RSS/Atom (200, 2026-10-09): Google DeepMind, OpenAI, Sakana AI, Google Research, Google AI blog, Microsoft Research, BAIR, NVIDIA, Hugging Face, Import AI, Interconnects, Latent Space, Ahead of AI, Last Week in AI, The Gradient, Lil'Log, AI Alignment Forum, ISAL.
- No feed found: Anthropic (`/rss.xml` and `/news/rss.xml` both 404; `sitemap.xml` with `lastmod` is available), Meta AI (`/blog/rss/` 404), The Batch (`/the-batch/feed/` 404).

### Cited Findings

| Source | Feed URL | Format / notes | Live source |
|---|---|---|---|
| Google DeepMind | `https://deepmind.google/blog/rss.xml` | RSS 2.0, lastBuildDate 2026-10-06. Its `atom:link` self-ref erroneously says example.com. | [link](https://deepmind.google/blog/rss.xml) |
| OpenAI | `https://openai.com/news/rss.xml` | RSS 2.0, 768 KB | [link](https://openai.com/news/rss.xml) |
| Anthropic | `https://www.anthropic.com/rss.xml` and `https://www.anthropic.com/news/rss.xml` | 404. `https://www.anthropic.com/sitemap.xml` returns 200 with `<lastmod>` per URL. | [rss 404](https://www.anthropic.com/rss.xml); [sitemap](https://www.anthropic.com/sitemap.xml) |
| Sakana AI | `https://sakana.ai/feed.xml` | Atom (Jekyll), mixed Japanese and English entries (`xml:lang`) | [link](https://sakana.ai/feed.xml) |
| Meta AI | `https://ai.meta.com/blog/rss/` | 404 | [link](https://ai.meta.com/blog/rss/) |
| Import AI | `https://jack-clark.net/feed/` and `https://importai.substack.com/feed` | Both 200 | [jack-clark.net](https://jack-clark.net/feed/); [substack](https://importai.substack.com/feed) |
| Interconnects | `https://www.interconnects.ai/feed` | Substack | [link](https://www.interconnects.ai/feed) |
| Latent Space | `https://www.latent.space/feed` | 1.3 MB, includes podcast | [link](https://www.latent.space/feed) |
| The Batch | `https://www.deeplearning.ai/the-batch/feed/` | 404 | [link](https://www.deeplearning.ai/the-batch/feed/) |
| Google Research | `https://research.google/blog/rss/` | | [link](https://research.google/blog/rss/) |
| Google AI blog | `https://blog.google/technology/ai/rss/` | 301 to `https://blog.google/innovation-and-ai/technology/ai/rss/` | [link](https://blog.google/technology/ai/rss/) |
| BAIR | `https://bair.berkeley.edu/blog/feed.xml` | | [link](https://bair.berkeley.edu/blog/feed.xml) |
| Lil'Log | `https://lilianweng.github.io/index.xml` | Latest post 2026-07-04, "Harness Engineering for Self-Improvement" | [link](https://lilianweng.github.io/index.xml) |
| Ahead of AI (Raschka) | `https://magazine.sebastianraschka.com/feed` | 2.7 MB | [link](https://magazine.sebastianraschka.com/feed) |
| Microsoft Research | `https://www.microsoft.com/en-us/research/feed/` | | [link](https://www.microsoft.com/en-us/research/feed/) |
| AI Alignment Forum | `https://www.alignmentforum.org/feed.xml` | | [link](https://www.alignmentforum.org/feed.xml) |
| The Gradient | `https://thegradient.pub/rss/` | | [link](https://thegradient.pub/rss/) |
| Last Week in AI | `https://lastweekin.ai/feed` | | [link](https://lastweekin.ai/feed) |
| NVIDIA Blog | `https://blogs.nvidia.com/feed/` | | [link](https://blogs.nvidia.com/feed/) |
| Hugging Face blog | `https://huggingface.co/blog/feed.xml` | Counts against HF "pages" bucket: 100 per 5 min anonymous | [link](https://huggingface.co/blog/feed.xml) |
| ISAL | `https://alife.org/feed/` | WordPress | [link](https://alife.org/feed/) |

### Inferences
- Several feeds are large: Ahead of AI 2.7 MB, Latent Space 1.3 MB, OpenAI 768 KB. Use conditional GET (`If-None-Match`/`If-Modified-Since`) and store only the item deltas.
- For Anthropic and Meta AI, the only non-scraping option is a daily `sitemap.xml` diff on `<lastmod>` (Anthropic), or an HTML index poll (Meta AI). Treat these as lower-reliability sources.
- Substack feeds (`/feed`) share a common format (`content:encoded` holds full post HTML). Store the link plus summary rather than the full HTML (see section 7).

### Gaps
- The Batch, Meta AI and Anthropic may have feeds at other paths. I did not guess further URLs, so whether such feeds exist is UNVERIFIED.
- EC/ALife-specific newsletters (e.g. SIGEVOlution) and individual lab blogs (Jeff Clune, Uber AI legacy) were not probed.

## 7. Licensing and terms that constrain storing abstracts, full text and model cards internally

### Takeaway
Per source:
- **Metadata from arXiv and OpenAlex** is CC0 and can be stored and transformed freely.
- **arXiv full text** may be stored for internal research use but not served.
- **Semantic Scholar data** may be stored only for internal non-commercial research or ML use, with attribution on any public use and no redistribution.
- **Hugging Face model cards** are user-owned content under each repo's license, with a broad license to other Hub users for public repos.
- **Crossref** has open metadata, but abstracts are publisher-supplied.
- **Blog and newsletter content** is copyrighted. Store the link, title and summary, not full text, unless it is clearly licensed otherwise.

### Cited Findings
- arXiv: metadata CC0. E-print content may be stored and used for personal or research purposes but not stored-and-served. Redistribution of e-prints "requires permission from the copyright holder". — [arXiv API ToU](https://info.arxiv.org/help/api/tou.html)
- arXiv: most submissions use the default license, which does not let arXiv grant others rights. Other licenses (e.g. CC-BY) are recorded in OAI-PMH metadata. Full-text indexes "must link back to arXiv for downloads". — [arXiv bulk data](https://info.arxiv.org/help/bulk_data.html)
- OpenAlex: all data CC0. — [OpenAlex help](https://help.openalex.org/api-reference/authentication.md)
- Semantic Scholar:
  - Internal non-commercial research or educational use, or "internal use solely for the purpose of training and evaluating machine learning models".
  - No resale, sublicensing or sharing of Data. Public uses must point back to S2 and display its name and logo.
  - Licensee bears copyright compliance because data is "from copyrighted sources".
  - Datasets downloads need an API key.
  - Sources: [S2 License](https://api.semanticscholar.org/license/); [S2 datasets latest](https://api.semanticscholar.org/datasets/v1/release/latest)
- Hugging Face: users own content. Public-repo content is licensed to "each User" perpetually, irrevocably and royalty-free "to use, display ...". The ToS is silent on automated access. — [HF ToS](https://huggingface.co/terms-of-service)
- Crossref: abuse of `mailto` (invalid emails) can lead to blocking. — [Crossref community post](https://community.crossref.org/t/refining-rest-api-limits-for-improved-stability-and-reliability/16137)

### Inferences
- Recommended catalog policy:
  - Store CC0 metadata (arXiv, OpenAlex) fully, including abstracts.
  - Store S2-derived fields (TLDRs, embeddings, citation counts) in a separately tagged table with `source_license='S2-API-License'` and an internal-only flag.
  - Store HF `cardData` plus card text with the repo's `license` tag.
  - Store blog items as link, title, published date, author and first-paragraph summary.
  - Keep arXiv PDF/HTML caches in a private object store with no external serving, and record per-paper license URIs so CC-BY items can be distinguished.
- The pipeline should carry a per-source `terms_version_seen` and `checked_at` field, because several terms changed in 2025-2026: Crossref in December 2025 and July 2026, OpenAlex in 2026, HF rate-limit tiers in September 2025, and arXiv OAI-PMH in March 2025.

### Gaps
- Crossref's official position on abstract licensing (CC0 metadata vs publisher-copyright abstracts) was not fetched verbatim. UNVERIFIED.
- OpenReview's terms on bulk reuse of reviews and abstracts were not fetched. UNVERIFIED.
- Lab blogs' individual terms (OpenAI, DeepMind) on automated fetching of RSS were not checked. RSS publication generally implies consent to syndication fetches, but that is not verified per site.
