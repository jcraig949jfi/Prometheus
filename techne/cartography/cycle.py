"""One 30-minute cartography cycle: steps A-I from the campaign brief.

RESTARTABILITY. Every cycle is a pure function of persisted state plus new network results, and
writes its fossil before returning. Killing the process between cycles costs the cycle in
flight and nothing else.

DIVERSITY PRESSURE IS ENFORCED MECHANICALLY, NOT BY GOOD INTENTIONS. `select_frontier` rotates
lanes by cycle index and prefers the least-visited lane, because the brief's warning -- do not
spend all 96 cycles on whatever produced the easiest early wins -- describes what an unguided
crawler does by default. Citation expansion in particular collapses onto highly-cited nodes if
you let it, which would rebuild a popularity ranking and call it a map.

WHAT A CYCLE MAY AND MAY NOT CONCLUDE. It may create genomes, propose claims, propose coverage
holes, and run deterministic predicates over stored evidence. It may NOT promote a coverage hole
on its own evidence alone -- promotion requires the independent-formulation test in
predicates.hole_is_persistent, which usually spans several cycles.
"""
from __future__ import annotations

import hashlib
import re
import traceback
from typing import Optional

from . import domain, predicates as P
from . import seeds, sources, store, taxonomy
from .schema import (
    Claim, ConfoundedClaim, CoverageHole, CycleRecord, EvidenceSpan, ResearchGenome,
    RetrievalAttempt, digest, now_iso,
)

#: Frontier lanes, rotated to keep the campaign off the path of least resistance.
FRONTIER_LANES = ("core", "collision", "awkward", "historical",
                  "citation_expand", "hole_kill", "confound_hunt")


def _gid(source_id: str) -> str:
    return "RG-" + hashlib.sha256((source_id or "").encode()).hexdigest()[:16]


def _cid(genome_id: str, kind: str, text: str) -> str:
    return "CL-" + hashlib.sha256((genome_id + kind + text[:200]).encode()).hexdigest()[:16]


def select_frontier(cycle: int, state: dict) -> dict:
    """STEP A. Pick what this cycle attacks, with diversity pressure.

    Lane rotation is deterministic in the cycle number so a restart resumes the same schedule
    rather than re-drawing and re-visiting. Within a lane, the least-recently-used query wins.
    """
    lane_counts = state.get("lane_counts", {})
    # Rotate, but skip a lane that is already over-represented relative to the least-used one.
    lane = FRONTIER_LANES[cycle % len(FRONTIER_LANES)]
    if lane_counts:
        least = min(lane_counts.get(l, 0) for l in FRONTIER_LANES)
        if lane_counts.get(lane, 0) > least + 2:
            lane = min(FRONTIER_LANES, key=lambda l: lane_counts.get(l, 0))

    if lane in ("core", "collision", "awkward", "historical"):
        pool = [s for s in seeds.all_seeds() if s["lane"] == lane]
        used = set(state.get("queries_used", []))
        fresh = [s for s in pool if s["query"] not in used]
        chosen = (fresh or pool)[cycle % max(1, len(fresh or pool))]
        return {"kind": lane, "target": chosen["query"]}

    if lane == "citation_expand":
        genomes = store.current("genomes")
        known = store.known_source_ids()
        # Prefer a genome whose references we have not yet walked, and among those the one with
        # the FEWEST citations -- the opposite of what an unguided crawler does, because the
        # highly-cited nodes are already the best-covered part of the map.
        cands = [g for g in genomes.values()
                 if g.get("citation_edges") and not g.get("_expanded")]
        cands.sort(key=lambda g: (g.get("cited_by_count") or 0))
        if cands:
            return {"kind": "citation_expand", "target": cands[0]["research_genome_id"]}
        return {"kind": "core", "target": seeds.CORE_SURFACE[cycle % len(seeds.CORE_SURFACE)]}

    if lane == "hole_kill":
        holes = [h for h in store.current("holes").values()
                 if h.get("status") == "COVERAGE_HOLE_CANDIDATE"]
        if holes:
            holes.sort(key=lambda h: h.get("n_formulations", 0))
            return {"kind": "hole_kill", "target": holes[0]["hole_id"]}
        return {"kind": "collision",
                "target": seeds.COLLISION_QUERIES[cycle % len(seeds.COLLISION_QUERIES)]}

    # confound_hunt
    return {"kind": "confound_hunt",
            "target": seeds.AWKWARD_QUERIES[cycle % len(seeds.AWKWARD_QUERIES)]}


def compile_genome(norm: dict, cycle: int, request_url: Optional[str] = None) -> tuple:
    """STEPS C+D. Turn a normalized source record into a genome plus proposed claims.

    Everything derived by lexical tagging is PROPOSED. The only things recorded as observed are
    the metadata the index returned and the verbatim abstract text, both with provenance.
    """
    sid = norm.get("source_id") or ""
    gid = _gid(sid)
    title = norm.get("title") or ""
    abstract = norm.get("abstract")

    spans = [EvidenceSpan(source_id=sid, scope="title", text=title,
                          url=norm.get("source_url")).as_dict()]
    if abstract:
        spans.append(EvidenceSpan(source_id=sid, scope="abstract", text=abstract,
                                  url=norm.get("source_url")).as_dict())

    blob = title + "\n" + (abstract or "")
    mech = taxonomy.tag_mechanisms(blob)
    bott = taxonomy.assign_bottleneck(mech)
    desc = taxonomy.descriptors_from(mech)

    dstatus, dreason = domain.classify(norm.get("concepts"), blob, norm.get("venue"))

    g = ResearchGenome(
        research_genome_id=gid,
        source_id=sid,
        title=title,
        year=norm.get("year"),
        authors=norm.get("authors") or [],
        venue=norm.get("venue"),
        source_url=norm.get("source_url"),
        doi=norm.get("doi"),
        citation_edges=norm.get("citation_edges") or [],
        cited_by_count=norm.get("cited_by_count"),
        open_access=norm.get("open_access"),
        fulltext_available=False,           # we hold abstracts at best; say so
        abstract_available=bool(abstract),
        concepts=norm.get("concepts") or [],
        domain_status=dstatus,
        domain_reason=dreason,
        bottleneck=bott,
        descriptors=desc,
        claimed_mechanism=sorted(mech.keys()),
        evidence_spans=spans,
        extraction_confidence={"mechanism_tagging": "lexical_proposed",
                               "evidence_scope": "abstract" if abstract else "title_only"},
        discovered_in_cycle=cycle,
        provenance={"request_url": request_url, "index": norm.get("_index", "openalex"),
                    "retrieved_at": now_iso()},
    )

    claims = []
    if abstract:
        # P1/P2/P3 run over the SAME stored spans a reader can re-check.
        for pname, pred, predicate_kind in (
                ("P1_claim_present", P.claim_present, "CLAIM_PRESENT"),
                ("P2_claim_supported", P.claim_supported, "CLAIM_SUPPORTED"),
        ):
            verdict, reason = pred(spans)
            if verdict == "CONFIRMED":
                claims.append(Claim(
                    claim_id=_cid(gid, predicate_kind, title),
                    research_genome_id=gid,
                    text=title,
                    predicate=predicate_kind,
                    evidence_type="AUTHOR_CLAIM",
                    adjudication="CONFIRMED",
                    adjudicated_by=pname,
                    adjudication_reason=reason,
                    evidence_spans=spans,
                    source_location="abstract",
                    cycle=cycle,
                ))
        v3, r3 = P.mechanism_isolated(spans)
        claims.append(Claim(
            claim_id=_cid(gid, "MECHANISM_ISOLATED", title),
            research_genome_id=gid,
            text=title,
            predicate="MECHANISM_ISOLATED",
            evidence_type=("DIRECT_OBSERVATION" if v3 == "CONFIRMED"
                           else "UNSUPPORTED_CAUSAL_ATTRIBUTION"),
            adjudication=v3,
            adjudicated_by="P3_mechanism_isolated",
            adjudication_reason=r3,
            evidence_spans=spans,
            source_location="abstract",
            cycle=cycle,
        ))
    return g, claims


def hunt_confounds(gid: str, spans: list, cycle: int) -> list:
    """STEP E (priority lane). Run P4 and P5 over stored evidence."""
    out = []
    v4, r4, dims = P.confounded_mechanism_claim(spans)
    if v4 == "CONFIRMED":
        v5, r5, migr = P.cost_migration(spans)
        out.append(ConfoundedClaim(
            confound_id="CF-" + hashlib.sha256((gid + "P4").encode()).hexdigest()[:16],
            research_genome_id=gid,
            claimed_mechanism="(attributed in abstract)",
            co_varying=dims,
            cost_migration=("; ".join(migr) if v5 == "CONFIRMED" else None),
            evidence_spans=spans,
            adjudication="CONFIRMED",
            adjudicated_by="P4_confounded_mechanism_claim"
                           + ("+P5_cost_migration" if v5 == "CONFIRMED" else ""),
            cycle=cycle,
        ))
    return out


#: Below this fraction of fully-classified genomes, an empty cell says nothing about the
#: literature. Proposing holes anyway manufactures candidates the campaign would then have to
#: spend cycles killing -- work generated by our own tagger's failure.
MIN_CLASSIFICATION_RATE = 0.25


def classification_rate() -> tuple:
    """(rate, n_classified, n_total) over genomes that carry abstract evidence.

    Title-only records are excluded from the denominator: a title genuinely cannot carry enough
    signal to place a paper on three mechanism axes, so counting them would blame the tagger
    for evidence it never had.
    """
    rows = [g for g in store.current("genomes").values()
            if any(sp.get("scope") == "abstract" and (sp.get("text") or "").strip()
                   for sp in (g.get("evidence_spans") or []))]
    if not rows:
        return 0.0, 0, 0
    ok = sum(1 for g in rows
             if "unknown" not in taxonomy.cell_of(g) and "B_UNASSIGNED" not in taxonomy.cell_of(g))
    return ok / len(rows), ok, len(rows)


def propose_holes(cycle: int, limit: int = 3) -> list:
    """STEP F. Find QD cells with no occupant. These are CANDIDATES, never discoveries.

    Only cells built from KNOWN axis values are proposed, and 'unknown' values are excluded --
    an empty cell whose coordinates are three unknowns is an artifact of our tagging, not a
    statement about the literature.
    """
    rate, n_ok, n_tot = classification_rate()
    if rate < MIN_CLASSIFICATION_RATE:
        # Refuse. An empty cell in a poorly-classified archive is a fact about the tagger.
        return []

    occupied = set()
    for g in store.current("genomes").values():
        occupied.add(taxonomy.cell_of(g))
    existing = {tuple(h["coordinates"]["cell"]) for h in store.current("holes").values()
                if h.get("coordinates", {}).get("cell")}

    out = []
    axes = taxonomy.QD_AXES
    for b in axes["bottleneck"]:
        for rep in axes["representation_family"]:
            if rep == "unknown":
                continue
            for sel in axes["selection_family"]:
                if sel == "unknown":
                    continue
                for ev in axes["evaluation_regime"]:
                    if ev == "unknown":
                        continue
                    cell = (b, rep, sel, ev)
                    if cell in occupied or cell in existing:
                        continue
                    out.append(CoverageHole(
                        hole_id="CH-" + hashlib.sha256(str(cell).encode()).hexdigest()[:16],
                        coordinates={"cell": list(cell),
                                     "axes": ["bottleneck", "representation_family",
                                              "selection_family", "evaluation_regime"]},
                        status="COVERAGE_HOLE_CANDIDATE",
                        confidence_in_absence="none_yet_no_retrieval_attempted",
                        archive_classification_rate=round(rate, 4),
                        archive_size_at_proposal=n_tot,
                        cycle=cycle,
                    ))
                    if len(out) >= limit:
                        return out
    return out


def attack_hole(hole: dict, cycle: int) -> tuple:
    """STEP E for holes. Try to KILL a coverage hole with independent retrieval.

    Runs distinct formulations against distinct indexes. A single relevant hit kills the hole,
    and killing is the desired outcome: the campaign's value is in how many apparent gaps
    evaporate, not in how many survive.
    """
    cell = tuple(hole["coordinates"]["cell"])
    forms = seeds.hole_formulations(cell)
    attempts = list(hole.get("retrieval_attempts") or [])
    found_ids = []
    notes = []

    source_order = ["openalex", "crossref", "arxiv", "dblp"]
    for i, f in enumerate(forms):
        src = source_order[i % len(source_order)]
        try:
            if src == "openalex":
                data = sources.openalex_search(f["query"], per_page=10)
                results = data.get("results", [])
                n_total = (data.get("meta") or {}).get("count", len(results))
                ids = [r.get("id") for r in results[:5]]
                url = data.get("_request_url")
            elif src == "crossref":
                data = sources.crossref_search(f["query"], rows=10)
                items = ((data.get("message") or {}).get("items") or [])
                n_total = (data.get("message") or {}).get("total-results", len(items))
                ids = [it.get("DOI") for it in items[:5]]
                url = data.get("_request_url")
            elif src == "arxiv":
                data = sources.arxiv_search(f["query"], max_results=10)
                n_total = data.get("total", 0)
                ids = [e["source_id"] for e in data["entries"][:5]]
                url = data.get("_request_url")
            else:
                data = sources.dblp_search(f["query"], hits=10)
                hits = sources.dblp_hits(data)
                n_total = len(hits)
                ids = [h["source_id"] for h in hits[:5]]
                url = data.get("_request_url")
            # RELEVANCE IS NOT RESULT COUNT. Every index returns something for every query.
            # A result counts as relevant only if its title carries mechanism vocabulary for
            # BOTH the representation and the selection axis of the cell.
            n_rel = _count_relevant(src, data, cell)
            att = RetrievalAttempt(query=f["query"], source=src, formulation=f["formulation"],
                                   n_results=int(n_total), n_relevant=n_rel,
                                   top_ids=[i for i in ids if i], url=url).as_dict()
            attempts.append(att)
            store.append("retrieval", att)
            if n_rel:
                found_ids.extend([i for i in ids if i][:3])
        except sources.SourceError as e:
            notes.append(str(e))
            continue

    verdict, reason = P.hole_is_persistent(attempts)
    hole["retrieval_attempts"] = attempts
    hole["n_formulations"] = len({a["formulation"] for a in attempts})
    if verdict == "REFUTED":
        hole["status"] = "KILLED_BY_RETRIEVAL"
        hole["killed_by"] = reason
        hole["nearest_prior_work"] = found_ids[:5]
        hole["confidence_in_absence"] = "none_cell_is_occupied"
    elif verdict == "CONFIRMED":
        hole["status"] = "PERSISTENT_COVERAGE_HOLE"
        hole["confidence_in_absence"] = ("weak_retrieval_protocol_only -- means no matching "
                                         "experiment FOUND, not that none exists")
    else:
        hole["confidence_in_absence"] = "insufficient_retrieval_" + reason
    return hole, notes


def _count_relevant(src: str, data: dict, cell: tuple) -> int:
    """A result is relevant only if its title tags BOTH the cell's representation and its
    selection mechanism. Counting raw hits would kill every hole instantly and counting zero
    would preserve every hole forever; this is the discriminating middle."""
    _b, rep, sel, _ev = cell
    titles = []
    if src == "openalex":
        titles = [(r.get("title") or "") for r in data.get("results", [])]
    elif src == "crossref":
        for it in ((data.get("message") or {}).get("items") or []):
            t = it.get("title") or []
            titles.append(t[0] if t else "")
    elif src == "arxiv":
        titles = [e.get("title") or "" for e in data.get("entries", [])]
    else:
        titles = [h.get("title") or "" for h in sources.dblp_hits(data)]

    n = 0
    for t in titles:
        tags = taxonomy.tag_mechanisms(t)
        if not tags:
            continue
        d = taxonomy.descriptors_from(tags)
        if d.get("representation_family") == rep and d.get("selection_family") == sel:
            n += 1
    return n


def run_cycle(cycle: int, state: dict, max_new: int = 12) -> tuple:
    """Execute one full cycle. Returns (CycleRecord, updated_state).

    Every exception is caught and recorded as a blocker rather than killing the campaign: a
    cycle that fails and says why is a fossil; a cycle that crashes the loop costs the
    remaining schedule.
    """
    rec = CycleRecord(cycle=cycle, started_at=now_iso())
    st = dict(state)
    st.setdefault("lane_counts", {})
    st.setdefault("queries_used", [])

    try:
        frontier = select_frontier(cycle, st)
        rec.frontier_kind = frontier["kind"]
        rec.frontier_target = frontier["target"]
        st["lane_counts"][frontier["kind"]] = st["lane_counts"].get(frontier["kind"], 0) + 1

        if frontier["kind"] == "hole_kill":
            holes = store.current("holes")
            hole = holes.get(frontier["target"])
            if hole:
                hole, notes = attack_hole(hole, cycle)
                store.upsert("holes", hole)
                rec.notes.extend(notes)
                if hole["status"] == "KILLED_BY_RETRIEVAL":
                    rec.holes_killed = 1
                rec.status = "OK"
            else:
                rec.status = "NULL"
                rec.notes.append("hole vanished from store")
        else:
            # STEP B -- acquire
            query = frontier["target"]
            if frontier["kind"] == "citation_expand":
                g = store.current("genomes").get(query)
                refs = (g or {}).get("citation_edges", [])[:max_new]
                known = store.known_source_ids()
                todo = [r for r in refs if r not in known][:max_new]
                rec.searches.append({"kind": "citation_expand", "of": query, "n": len(todo)})
                created = 0
                for wid in todo:
                    try:
                        work = sources.openalex_work(wid)
                        norm = sources.openalex_normalize(work)
                        norm["_index"] = "openalex"
                        dstat, dreas = domain.classify(
                            norm.get("concepts"),
                            (norm.get("title") or "") + " " + (norm.get("abstract") or "")[:600],
                            norm.get("venue"))
                        if domain.is_rejected(dstat):
                            store.append("rejected", {"source_id": norm["source_id"],
                                                      "reason": "off_domain:" + dreas,
                                                      "title": norm.get("title"),
                                                      "cycle": cycle})
                            rec.sources_rejected += 1
                            continue
                        genome, claims = compile_genome(norm, cycle, work.get("_request_url"))
                        store.upsert("genomes", genome)
                        store.append_many("claims", claims)
                        rec.claims_created += len(claims)
                        created += 1
                        for cf in hunt_confounds(genome.research_genome_id,
                                                 genome.evidence_spans, cycle):
                            store.append("confounds", cf)
                            rec.confounds_found += 1
                    except sources.SourceError as e:
                        rec.blockers.append(str(e))
                rec.genomes_created = created
                rec.sources_new = created
                if g:
                    g["_expanded"] = True
                    store.upsert("genomes", g)
            else:
                st["queries_used"].append(query)
                data = sources.openalex_search(query, per_page=max_new)
                results = data.get("results", [])
                att = RetrievalAttempt(
                    query=query, source="openalex", formulation="seed_" + frontier["kind"],
                    n_results=(data.get("meta") or {}).get("count", len(results)),
                    n_relevant=len(results),
                    top_ids=[r.get("id") for r in results[:5]],
                    url=data.get("_request_url")).as_dict()
                store.append("retrieval", att)
                rec.searches.append(att)

                known = store.known_source_ids()
                created = 0
                for work in results:
                    norm = sources.openalex_normalize(work)
                    norm["_index"] = "openalex"
                    if norm["source_id"] in known:
                        rec.sources_rejected += 1
                        continue
                    dstat, dreas = domain.classify(
                        norm.get("concepts"),
                        (norm.get("title") or "") + " " + (norm.get("abstract") or "")[:600],
                        norm.get("venue"))
                    if domain.is_rejected(dstat):
                        # Homonym contamination is the measured failure this gate stops:
                        # 22.7% of the first 97 genomes were off-domain, and one had already
                        # reached the confound ledger.
                        store.append("rejected", {"source_id": norm["source_id"],
                                                  "reason": "off_domain:" + dreas,
                                                  "title": norm.get("title"), "cycle": cycle})
                        rec.sources_rejected += 1
                        continue
                    # NO LONGER REJECTED FOR LACKING AN ABSTRACT.
                    #
                    # Discarding abstract-less records threw away 45 papers -- 33% the size of
                    # the kept corpus -- and they were overwhelmingly CORE in-domain work:
                    # Fogel's "Evolutionary computation: toward a new philosophy of machine
                    # intelligence", Eiben & Smith's "From evolutionary computation to the
                    # evolution of things", three canonical lexicase papers, Coello Coello's
                    # multi-objective text, Jin's fitness-approximation survey.
                    #
                    # Abstract availability in OpenAlex correlates with publisher -- books and
                    # proceedings often carry none -- so rejecting on it biased the archive by
                    # venue type, which SYSTEMATICALLY OVERSTATED coverage holes: cells looked
                    # empty when their occupants had simply been discarded. That defect attacks
                    # the campaign's central product directly.
                    #
                    # Title-only records are therefore admitted to the ARCHIVE (a cell they
                    # occupy is occupied) and carry abstract_available=False, which stops every
                    # claim predicate from running on them.
                    genome, claims = compile_genome(norm, cycle, data.get("_request_url"))
                    store.upsert("genomes", genome)
                    store.append_many("claims", claims)
                    rec.claims_created += len(claims)
                    created += 1
                    for cf in hunt_confounds(genome.research_genome_id,
                                             genome.evidence_spans, cycle):
                        store.append("confounds", cf)
                        rec.confounds_found += 1
                rec.genomes_created = created
                rec.sources_new = created

        # STEP F -- propose coverage holes from the updated archive
        new_holes = propose_holes(cycle, limit=3)
        for h in new_holes:
            store.append("holes", h)
        rec.holes_proposed = len(new_holes)

        rec.claims_adjudicated = rec.claims_created
        if rec.genomes_created == 0 and rec.holes_killed == 0 and rec.status == "OK":
            rec.status = "NULL"

    except Exception as e:                                            # noqa: BLE001
        rec.status = "BLOCKED"
        rec.blockers.append(type(e).__name__ + ": " + str(e)[:200])
        rec.failures.append(traceback.format_exc()[-800:])

    rec.ended_at = now_iso()
    rec.artifact_digest = digest(rec.as_dict())
    store.write_cycle(rec)
    st["last_cycle"] = cycle
    st["last_cycle_at"] = rec.ended_at
    return rec, st
