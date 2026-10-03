"""The one-line changes two readers made to version three of the harness in the final round, carried over
to the current code. Generated from their scripts (attack/closure_reader/scripts_final/p32_fresh_mutations.py
and attack/second_reader/scripts_final/first_sight.py); the reader's own id is in brackets. Where the code a
change touched was rewritten afterwards, the same change is made to the new code."""

FINAL = [
    ('X01 (W01) G3: the impostor blocks may repeat the first block of seeds (only the further blocks are compared)', 'rulers.py', [
        ('    every = [s for block in [seeds] + list(blocks) for s in block]',
         '    every = [s for block in list(blocks) for s in block]')]),
    ('X02 (W02) G5: a physics with no known answer counts toward the three a shared ruler needs', 'rulers.py', [
        ('        if len(known) < MIN_PHYSICS:',
         '        if len(table) < MIN_PHYSICS:')]),
    ('X03 (W03) G6.restart: the first step after the cut is not compared', 'torture.py', [
        ('            if (whole["answer"], whole["trace"][at + 1:], whole["final"]) != (cut["answer"], cut["trace"][at + 1:],',
         '            if (whole["answer"], whole["trace"][at + 2:], whole["final"]) != (cut["answer"], cut["trace"][at + 2:],')]),
    ('X04 (W04) G8: the clock table sees two bits of the clock, not three', 'torture.py', [
        ('"CLOCK": (probe[1] & 7,)',
         '"CLOCK": (probe[1] & 3,)')]),
    ('X05 (W05) G7.report: a stated bound above 1 is accepted', 'search.py', [
        ('        elif not _number(bound) or not zero_hit_upper(n) - 5e-5 <= bound < 1:',
         '        elif not _number(bound) or not zero_hit_upper(n) - 5e-5 <= bound:')]),
    ('X06 (W06) G7.calibration: the panel loses its fifth cell (VALLEY, strict, cold)', 'search.py', [
        ('         ("ASCENT", "STRICT", "COLD", 0), ("VALLEY", "STRICT", "COLD", 0))',
         '         ("ASCENT", "STRICT", "COLD", 0))')]),
    ('X07 (W07) G10.setting: placeholders are refused in lower case only', 'stats.py', [
        ('    return v is None or (isinstance(v, str) and v.strip().lower() in PLACEHOLDERS)',
         '    return v is None or (isinstance(v, str) and v.strip() in PLACEHOLDERS)')]),
    ('X08 (W08) G10.setting: a power above 1 is accepted', 'audits.py', [
        ('0.99 <= v <= 1.0',
         '0.99 <= v')]),
    ('X09 (W09) G10.setting: true and false count as numbers', 'audits.py', [
        ('    return isinstance(v, (int, float)) and not isinstance(v, bool)',
         '    return isinstance(v, (int, float))')]),
    ('X10 (W10) G10.contrast: a field written down in one cell only is not compared', 'audits.py', [
        ('    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))',
         '    differ = sorted(k for k in set(a) & set(b) if a.get(k) != b.get(k))')]),
    ('X11 (W11) G9.arms: two arms with one series are allowed; three are not', 'audits.py', [
        ('    merged = [g for g in groups if len(g) > 1 and set(g) != set(exempt)]',
         '    merged = [g for g in groups if len(g) > 2 and set(g) != set(exempt)]')]),
    ('X12 (W12) G12.render: the setting hash depends on the order the choices were typed in', 'claims.py', [
        ('    return hashlib.sha256(json.dumps(setting, sort_keys=True).encode("ascii")).hexdigest()',
         '    return hashlib.sha256(json.dumps(setting, sort_keys=False).encode("ascii")).hexdigest()')]),
    ('X13 (W13) G2: a bound of exactly 0 or 1 is accepted', 'stats.py', [
        ('    if not (is_count(n) and n > 0 and 0 < p0 < 1 and 0 < alpha < 1 and 0 < p_positive <= 1):',
         '    if not (is_count(n) and n > 0 and 0 <= p0 <= 1 and 0 < alpha < 1 and 0 < p_positive <= 1):')]),
    ('X14 (W14) G8: the upper side of the equivalence test is run at alpha, not alpha/2', 'stats.py', [
        ('    below = tail_le(n, k, min(center + margin, 1.0)) <= alpha / 2 ',
         '    below = tail_le(n, k, min(center + margin, 1.0)) <= alpha ')]),
    ("X15 (W16) interchange: 'carried somewhere that was not moved' is reported as NEGATIVE", 'rulers.py', [
        ('            ("INVERTED", "EXCLUDES"): "NOT_MOVED", ("EXCLUDES", "INVERTED"): "NOT_MOVED"}.get((a, b), "NEGATIVE")',
         '            ("INVERTED", "EXCLUDES"): "NEGATIVE", ("EXCLUDES", "INVERTED"): "NOT_MOVED"}.get((a, b), "NEGATIVE")')]),
    ('X16 (W18) ladder: the control arm is ignored when the two arms are read together', 'ladder.py', [
        ('    if control["answer"] == "CARRIED":',
         '    if False:')]),
    ('X17 (W19) G12: level() never reports L4', 'claims.py', [
        ('    for lv in (1, 2, 3, 4):',
         '    for lv in (1, 2, 3):')]),
    ('X18 (W20) ladder: the Hoeffding margin with n in place of 2n', 'ladder.py', [
        ('    threshold = H16 + N * sqrt(log(1 / alpha) / (2 * n))',
         '    threshold = H16 + N * sqrt(log(1 / alpha) / n)')]),
    ('X19 (W21) G3: an empty panel is not refused', 'rulers.py', [
        ('    if not panel or any(pos is None or imp is None for pos, imp in panel.values()):',
         '    if any(pos is None or imp is None for pos, imp in panel.values()):')]),
    ('X20 (W22) G10.setting: the wrong-history choice is no longer one of the nine', 'audits.py', [
        ('SETTING = ("cost", "later_families", "content_reset", "sham", "family_A", "wrong_history", "effect_threshold",',
         'SETTING = ("cost", "later_families", "content_reset", "sham", "family_A", "effect_threshold",')]),
    ('X21 (W23) G7.report: the founders are compared as sets, so a founder may be reported twice', 'search.py', [
        ('        if sorted(p["seeds"]) != sorted(seeds):',
         '        if set(p["seeds"]) != set(seeds):')]),
    ('X22 (W24) G11: a discovery and a confirmation may share their panel if their seeds differ', 'claims.py', [
        ('    if d["panel_sha256"] == c["panel_sha256"]:',
         '    if d["panel_sha256"] == c["panel_sha256"] and set(d["seeds"]) & set(c["seeds"]):')]),
    ('X23 (W26) G9.clauses: a clause is isolated if the others hold in 21 of 24', 'audits.py', [
        ('        table[c][cell] <= FAILS_AT and all(table[d][cell] >= HOLDS_AT for d in names if d != c) for cell in cell_names))',
         '        table[c][cell] <= FAILS_AT and all(table[d][cell] >= HOLDS_AT - 1 for d in names if d != c) for cell in cell_names))')]),
    ('X24 (W28) G4.entry: the impostor is judged on the first 48 seeds', 'rulers.py', [
        ('    on_positive, on_impostor = exclusion_ruler(pair[0], seeds), exclusion_ruler(pair[1], seeds)',
         '    on_positive, on_impostor = exclusion_ruler(pair[0], seeds), exclusion_ruler(pair[1], seeds[:48])')]),
    ('X25 (W27) G6.reset: the earlier episode is run on the same seed as the later one', 'torture.py', [
        ('                episode(w, org, seed, earlier)',
         '                episode(w, org, seed + 1, earlier)')]),
    ('X26 (W29) G1.cell: the highest count of a verdict table is not checked', 'registration.py', [
        ('    for count in range(n + 1):\n        got = [o for lo, hi, o in rule if lo <= count <= hi]',
         '    for count in range(n):\n        got = [o for lo, hi, o in rule if lo <= count <= hi]')]),
    ('Y01 (S01) stats.upper_bound: the upper end of a design rate at its median, not at 99%', 'stats.py', [
        ('        if tail_le(n, k, mid) < 1 - conf:',
         '        if tail_le(n, k, mid) < 1 - conf / 2:')]),
    ('Y02 (S02) stats.is_count: a float counts as a count', 'stats.py', [
        ('    return isinstance(v, int) and not isinstance(v, bool) and v >= 0',
         '    return isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0')]),
    ("Y03 (S03) G2: the negative's probability is taken up to the weak positive's critical count even where that is a yes", 'stats.py', [
        ('    said_no = 0.0 if no is None else tail_le(n, min(no, k - 1), p0)',
         '    said_no = 0.0 if no is None else tail_le(n, no, p0)')]),
    ('Y04 (S04) G2: power computed one count below the critical count', 'stats.py', [
        ('    power = tail_ge(n, k, p_positive)',
         '    power = tail_ge(n, k - 1, p_positive)')]),
    ('Y05 (S05) equivalence: the upper margin is not tested', 'stats.py', [
        ('tail_le(n, k, min(center + margin, 1.0))',
         'tail_le(n, k, 1.0)')]),
    ('Y06 (S06) consistent: each side at alpha, not alpha/2', 'stats.py', [
        ('    return tail_ge(n, k, p) > alpha / 2 and tail_le(n, k, p) > alpha / 2',
         '    return tail_ge(n, k, p) > alpha and tail_le(n, k, p) > alpha')]),
    ('Y07 (S07) G2: more design hits than design runs accepted', 'stats.py', [
        ('    if not (is_count(design_n) and design_n > 0 and is_count(design_hits) and design_hits <= design_n):',
         '    if not (is_count(design_n) and design_n > 0 and is_count(design_hits)):')]),
    ('Y08 (G01) G1.cell: attainability taken at the lower end of the design interval only', 'registration.py', [
        ('                for rate in (stats.lower_bound(h, n), stats.upper_bound(h, n)))',
         '                for rate in (stats.lower_bound(h, n),))')]),
    ('Y09 (G02) G1.cell: more design hits than design units accepted', 'registration.py', [
        ('or not is_count(n) or n == 0 or h > n:',
         'or not is_count(n) or n == 0:')]),
    ('Y10 (G03) G1.cell: the registration clock is not type-checked', 'registration.py', [
        ('    if cell.get("registered_at") is not None and not is_count(cell["registered_at"]):',
         '    if False:')]),
    ('Y11 (G04) G1.cell: an empty list or dict counts as a registered field', 'registration.py', [
        ('    missing = [k for k in REQUIRED if cell.get(k) in (None, "", [], {}, ())]',
         '    missing = [k for k in REQUIRED if cell.get(k) in (None, "")]')]),
    ('Y12 (G05) G1.receipt: a receipt need not list its seeds to be checked', 'registration.py', [
        ('    missing = [k for k in ("source_sha256", "seeds", "ran_at") if receipt.get(k) in (None, "", [])]',
         '    missing = [k for k in ("source_sha256", "ran_at") if receipt.get(k) in (None, "", [])]')]),
    ('Y13 (G06) G1.receipt: line endings are not normalised before hashing', 'registration.py', [
        ('    return hashlib.sha256(source.replace(b"\\r\\n", b"\\n")).hexdigest()',
         '    return hashlib.sha256(source).hexdigest()')]),
    ('Y14 (V01) G0: UNQUALIFIED outranks BLOCKED', 'verdict.py', [
        ('_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 2, INDETERMINATE: 1, PASS: 0}',
         '_RANK = {FAIL: 4, BLOCKED: 2, UNQUALIFIED: 3, INDETERMINATE: 1, PASS: 0}')]),
    ('Y15 (V02) G0: nothing to combine is a PASS', 'verdict.py', [
        ('        return Result(gate, BLOCKED, "no results to combine")',
         '        return Result(gate, PASS, "no results to combine")')]),
    ('Y16 (V03) G0: a sixth verdict is accepted', 'verdict.py', [
        ('        if verdict not in ALL:',
         '        if False:')]),
    ('Y17 (U01) G3: the registered threshold at 48 is dropped', 'rulers.py', [
        ('EDGES = {51: "POSITIVE", 50: "UNDECIDED", 48: "UNDECIDED", 47: "NEGATIVE", 14: "NEGATIVE", 13: "INVERTED"}',
         'EDGES = {51: "POSITIVE", 50: "UNDECIDED", 47: "NEGATIVE", 14: "NEGATIVE", 13: "INVERTED"}')]),
    ('Y18 (U02) interchange: the state is moved at step 5, not step 3', 'rulers.py', [
        ('def _interchange(make, seeds, grab, put, at=3):',
         'def _interchange(make, seeds, grab, put, at=5):')]),
    ('Y19 (U03) interchange: an undecided count is called NEGATIVE', 'rulers.py', [
        ('        return "UNDECIDED"',
         '        return "NEGATIVE"')]),
    ('Y20 (U04) interchange: crossed-inverted with same-follows is called NEGATIVE, not NOT_MOVED', 'rulers.py', [
        ('("INVERTED", "EXCLUDES"): "NOT_MOVED", ("EXCLUDES", "INVERTED"): "NOT_MOVED"}',
         '("INVERTED", "EXCLUDES"): "NEGATIVE", ("EXCLUDES", "INVERTED"): "NOT_MOVED"}')]),
    ('Y21 (T01) G6.reset: the mark left on the environment is not compared', 'torture.py', [
        ('        return r["answer"], r["trace"], r["final"][0], r["final"][1]',
         '        return r["answer"], r["trace"], r["final"][0]')]),
    ('Y22 (T02) G6.restart: the step right after the cut is not compared', 'torture.py', [
        ('            if (whole["answer"], whole["trace"][at + 1:], whole["final"]) != (cut["answer"], cut["trace"][at + 1:],',
         '            if (whole["answer"], whole["trace"][at + 2:], whole["final"]) != (cut["answer"], cut["trace"][at + 2:],')]),
    ('Y23 (T03) G6.restart: no cut after the first step', 'torture.py', [
        ('        for at in range(len(whole["trace"])):',
         '        for at in range(1, len(whole["trace"])):')]),
    ('Y24 (T04) G6.observer: only the first six seeds are run', 'torture.py', [
        ('        return [w.episode(make(), seed, observer=observer) for seed in seeds]',
         '        return [w.episode(make(), seed, observer=observer) for seed in seeds[:6]]')]),
    ('Y25 (R01) G7.report: founders compared as a set (order and repeats ignored)', 'search.py', [
        ('        if sorted(p["seeds"]) != sorted(seeds):',
         '        if set(p["seeds"]) != set(seeds):')]),
    ('Y26 (R02) G7.report: fewer hits reported than the search had is accepted', 'search.py', [
        ('        if replayed != p["hits"]:',
         '        if replayed < p["hits"]:')]),
    ('Y27 (R03) G7.report: positive control needed at 0.85, not 0.99', 'search.py', [
        ('            if control < 0.99:',
         '            if control < 0.85:')]),
    ('Y28 (R04) G7.report: a bound up to 0.005 below what the founders warrant is accepted', 'search.py', [
        ('- 5e-5 <= bound < 1:',
         '- 5e-3 <= bound < 1:')]),
    ('Y29 (R05) G7.calibration: the needle repair cell is dropped from the panel', 'search.py', [
        ('CELLS = (("NEEDLE", "NEUTRAL", "COLD", 0), ("NEEDLE", "NEUTRAL", "REPAIR", 1), ("VALLEY", "NEUTRAL", "REPAIR", 1),',
         'CELLS = (("NEEDLE", "NEUTRAL", "COLD", 0), ("VALLEY", "NEUTRAL", "REPAIR", 1),')]),
    ('Y30 (R06) G7.report: one policy that crosses neutral steps is enough for a null', 'search.py', [
        ('        if len(report["policies"]) < 2 or "CROSSES_NEUTRAL_STEPS" not in kinds:',
         '        if "CROSSES_NEUTRAL_STEPS" not in kinds:')]),
    ('Y31 (A01) G9.arms: with fewer than 22 replicates no two arms are ever one series', None, 'GONE: the audit now refuses any number of replicates other than 24, so the two forms are the same'),
    ('Y32 (A02) G9.arms: two arms with one series are tolerated; three are not', 'audits.py', [
        ('    merged = [g for g in groups if len(g) > 1 and set(g) != set(exempt)]',
         '    merged = [g for g in groups if len(g) > 2 and set(g) != set(exempt)]')]),
    ('Y33 (A03) G9.clauses: run 3 audited at factor 3, not its registered 2', 'audits.py', [
        ('def clauses_run3(o, factor=2):',
         'def clauses_run3(o, factor=3):')]),
    ('Y34 (A04) G10.setting: placeholders are matched case-sensitively', 'stats.py', [
        ('    return v is None or (isinstance(v, str) and v.strip().lower() in PLACEHOLDERS)',
         '    return v is None or (isinstance(v, str) and v.strip() in PLACEHOLDERS)')]),
    ('Y35 (A05) G10.setting: power has no upper limit', 'audits.py', [
        ('(_number(v) and 0.99 <= v <= 1.0)',
         '(_number(v) and 0.99 <= v)')]),
    ('Y36 (A06) G10.setting: the horizon need not be a whole number', 'audits.py', [
        ('(_number(v) and v == int(v) and v >= 1)',
         '(_number(v) and v >= 1)')]),
    ('Y37 (A07) G10.contrast: a field written in one cell only is not a difference', 'audits.py', [
        ('    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))',
         '    differ = sorted(k for k in set(a) & set(b) if a.get(k) != b.get(k))')]),
    ('Y38 (A08) G10.ruler: a cell verdict other than PASS or FAIL is read as NEGATIVE', 'audits.py', [
        ('            return {"PASS": "POSITIVE", "FAIL": "NEGATIVE"}[data["cells"][key]["verdict"]]',
         '            return {"PASS": "POSITIVE", "FAIL": "NEGATIVE"}.get(data["cells"][key]["verdict"], "NEGATIVE")')]),
    ('Y39 (A09) G10.ruler: RULER_NOT_APPLICABLE is no longer a guard', 'audits.py', [
        ('GUARDS = ("INHERITED_OR_LEAK", "RULER_NOT_APPLICABLE")',
         'GUARDS = ("INHERITED_OR_LEAK",)')]),
    ('Y40 (A10) G10.ruler: a member run here and also elsewhere is reported as not run here', 'audits.py', [
        ('    elsewhere = sorted({r[0] for r in runs if claim in r[3] and r[1] != setting} - {r[0] for r in here})',
         '    elsewhere = sorted({r[0] for r in runs if claim in r[3] and r[1] != setting})')]),
    ('Y41 (C01) G11: the opening clock is not type-checked', 'claims.py', [
        ('            and is_count(record["rule_fixed_at"]) and is_count(record["confirmation_opened_at"])):',
         '            and is_count(record["rule_fixed_at"])):')]),
    ('Y42 (C02) G11: a side needs no generator hash', 'claims.py', [
        ('    part = ("seeds", "panel_sha256", "generator_sha256")',
         '    part = ("seeds", "panel_sha256")')]),
    ('Y43 (C03) G12.render: the setting hash depends on key order', 'claims.py', [
        ('json.dumps(setting, sort_keys=True)',
         'json.dumps(setting, sort_keys=False)')]),
    ('Y44 (C04) G11: an empty string counts as a custody field', 'claims.py', [
        ('    missing = [k for k in CUSTODY_FIELDS if record.get(k) is None or (isinstance(record[k], str) and not record[k].strip())]',
         '    missing = [k for k in CUSTODY_FIELDS if record.get(k) is None]')]),
    ('Y45 (L01) ladder: certificate at alpha 0.01, not 1e-6', 'ladder.py', [
        ('def certificate(per_life, alpha=1e-6):',
         'def certificate(per_life, alpha=1e-2):')]),
    ('Y46 (L02) ladder: the control is ignored when the ninth pair is CARRIED', 'ladder.py', [
        ('    if control["answer"] == "CARRIED":',
         '    if control["answer"] == "CARRIED" and full["answer"] != "CARRIED":')]),
    ('Y47 (L03) ladder: in the control the ninth pair too comes from the other key', 'ladder.py', [
        ('            bases, moves = other if (control and (j, k) != UNSEEN) else own',
         '            bases, moves = other if control else own')]),
    ('Y48 (W01) score: a fresh world for every seed', 'retain1.py', [
        ('(w.episode(make(), s)))',
         '(World(**world).episode(make(), s)))')]),
    ('Y49 (W02) world: the final state does not hold the mark', 'retain1.py', [
        ('                "final": (org.native(), self.mark, self.draws, self.episodes)}',
         '                "final": (org.native(), None, self.draws, self.episodes)}')]),
    ('Y50 (W03) world: the trajectory does not hold the value delivered', 'retain1.py', [
        ('            trace.append((obs.kind, obs.value, obs.clock, obs.mark, after_step, org.native()))',
         '            trace.append((obs.kind, None, obs.clock, obs.mark, after_step, org.native()))')]),
    ('Y51 (M01) GM: a mutant that passes is not an escape', 'meta.py', [
        ('        escapes = [name for name, r, _ in mutant_results if r.verdict == PASS]',
         '        escapes = [name for name, r, _ in mutant_results if r.verdict == PASS and False]')]),
    ('Y52 (M02) GM: a sound case refused as BLOCKED, UNQUALIFIED or INDETERMINATE is no false accusation', 'meta.py', [
        ('        false_alarms = [r.reason or r.verdict for r in clean_results if r.verdict != PASS]',
         '        false_alarms = [r.reason or r.verdict for r in clean_results if r.verdict == FAIL]')]),
    ('Y53 (M03) GM: the missing-field mutant tries the first eight fields only', 'meta.py', [
        ('    open_ = [f for f in fields if check(make(**{f: None})).verdict != BLOCKED]',
         '    open_ = [f for f in fields[:8] if check(make(**{f: None})).verdict != BLOCKED]')]),
    ('Y54 (M04) GM: the kind-facet mutant tries the first three kinds only', 'meta.py', [
        ('    open_ = ["%s.%s" % (k, f) for k, fs in sorted(KIND_FACETS.items()) for f in fs',
         '    open_ = ["%s.%s" % (k, f) for k, fs in sorted(KIND_FACETS.items())[:3] for f in fs')]),
]
