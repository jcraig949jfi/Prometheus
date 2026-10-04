"""Instrument selection for v2b experiments: the tribunal (T4 v1 historical | v1a repaired) and the ruler
(v2 historical | v2.1 repaired). Each experiment freezes its choice in its AMENDMENT, and the choice enters
APPARATUS_ID.

Two independent tribunal evaluation paths exist, and conformance requires them to agree:
  ARTIFACT  the emitted-artifact path: the program is emitted as module bytes (a17.M.artifact_for), loaded
            into a fresh Recipient, and scored by the Tribunal class. This is the path historical verdicts used.
  DIRECT    a program-level scorer (tribunal_t4_v1a.direct_score) that runs the program on the same battery
            inputs. It is much faster.
`qualifier(..., path="BOTH")` returns a function that scores with DIRECT and, on every positive, confirms with
ARTIFACT. A disagreement raises EvaluatorDisagreement, which is a TECHNICAL_FAILURE, never a science outcome.
"""
import paths  # noqa: F401
import a17
import tribunal_t4 as T4v1
import tribunal_t4_v1a as T4v1a

TRIBUNALS = {"v1": T4v1, "v1a": T4v1a}


class EvaluatorDisagreement(Exception):
    pass


def tribunal_class(version):
    return T4v1.TribunalT4 if version == "v1" else T4v1a.TribunalT4v1a


def qualify_artifact(prov, name, prog, version="v1a"):
    T4v1.use_provider(prov)
    a17.M.use_provider(prov)
    art = a17.M.artifact_for(name, tuple(prog), a17.EMITTER)
    cls = tribunal_class(version)
    tr = cls.after_freeze(art, name)    # keeps the historical boundary check (frozen-generation artifact)
    sc = tr.score(art)
    return bool(tr.qualified(sc)), sc


def qualify_direct(prov, name, prog, version="v1a"):
    T4v1.use_provider(prov)
    witness = prov.witness(name)
    r = T4v1a.direct_score(tuple(prog), name, witness, version="v1" if version == "v1" else "v1a")
    return bool(r["qualified"]), r


def qualifier(prov, name, version="v1a", path="BOTH", log=None):
    """Return prog -> bool. With path BOTH, every DIRECT positive is confirmed through ARTIFACT, and a sample of
    DIRECT negatives can be confirmed by the caller through confirm_negative."""
    def q(prog):
        d, _ = qualify_direct(prov, name, prog, version)
        if path == "DIRECT":
            return d
        if path == "ARTIFACT":
            return qualify_artifact(prov, name, prog, version)[0]
        if d:
            a, _ = qualify_artifact(prov, name, prog, version)
            if a != d:
                raise EvaluatorDisagreement("%s %s: direct=%s artifact=%s" % (name, prog, d, a))
            if log is not None:
                log.append({"family": name, "program": list(prog), "direct": d, "artifact": a})
        return d
    return q


def ruler(version="v2.1"):
    if version == "v2":
        import ruler_v2 as R
    else:
        import ruler_v21 as R
    return R


def equal_extensional(s, t, version="v2.1"):
    """Schema equality under the ruler's closure: literal EQUAL, or EQUAL_C under re-expression closure in
    v2.1. This is the equality used by Control.check_distinct."""
    R = ruler(version)
    if s == t:
        return True
    rel = R.relations(s, t)
    return bool(rel.get("EQUAL") or rel.get("EQUAL_C") or rel.get("EQUAL_ANY"))
