"""Credential resolution, in one place, so no seat reinvents it.

A seat should never write its own key-loading code. Three ordered
sources, first hit wins:

  1. PROMETHEUS_RUNPOD_KEY_FILE  -- a path, for anyone who keeps the key
     somewhere of their own choosing
  2. RUNPOD_API_KEY              -- already in the environment
  3. the host default            -- the operator's existing key file

The value is never returned to a caller that only needs to know whether
a credential EXISTS, never logged, never placed on argv, and never
written to a manifest, plan or receipt. `describe()` is the safe thing
to print: it says where the key came from and how long it is, and
nothing else.

Hardcoded drive letters are a base-role violation
(RESPONSIBILITIES s2), so the host default lives in one named constant
here rather than being copied into every orchestrator, and it is the
LAST resort rather than the only one. The existing AETH-01/02
orchestrators each inline that path; this module is what they should
converge on.
"""

import os
import re

KEY_ENV = "RUNPOD_API_KEY"
KEY_FILE_ENV = "PROMETHEUS_RUNPOD_KEY_FILE"
# Operator's host convention. Referenced, not assumed: it is tried last
# and its absence is not an error until a credential is actually needed.
HOST_DEFAULT_KEY_FILE = r"C:\runpod_key\keys.txt"

_KEY_SHAPE = re.compile(r"^rpa_[A-Za-z0-9]{16,}$")


class CredentialError(RuntimeError):
    pass


def _from_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                token = line.strip()
                if _KEY_SHAPE.match(token):
                    return token
    except OSError:
        return None
    return None


def resolve(required=True):
    """Return (key, source_label). The key is a secret: do not log it."""
    path = os.environ.get(KEY_FILE_ENV)
    if path:
        key = _from_file(path)
        if key:
            return key, "%s=%s" % (KEY_FILE_ENV, path)
        if required:
            raise CredentialError(
                "%s points at %s but no rpa_ key was found there"
                % (KEY_FILE_ENV, path))

    env_key = os.environ.get(KEY_ENV, "").strip()
    if env_key:
        if not _KEY_SHAPE.match(env_key):
            raise CredentialError(
                "%s is set but does not look like a RunPod key; refusing to "
                "use it rather than sending a malformed credential" % KEY_ENV)
        return env_key, "environment %s" % KEY_ENV

    key = _from_file(HOST_DEFAULT_KEY_FILE)
    if key:
        return key, "host default key file"

    if required:
        raise CredentialError(
            "no RunPod credential found. Set %s to a file containing an rpa_ "
            "key, or export %s." % (KEY_FILE_ENV, KEY_ENV))
    return None, "none"


def available():
    """True if a credential exists, WITHOUT returning it."""
    try:
        key, _source = resolve(required=False)
        return key is not None
    except CredentialError:
        return False


def describe():
    """Safe to print, log and commit: provenance and length, never value."""
    try:
        key, source = resolve(required=False)
    except CredentialError as exc:
        return {"available": False, "error": str(exc)}
    if key is None:
        return {"available": False, "source": source}
    return {"available": True, "source": source, "length": len(key),
            "prefix": key[:4]}


def install_into_environ():
    """Put the key in os.environ for the qualified RunPod client.

    The existing client reads RUNPOD_API_KEY at construction. Doing this
    in one audited place is better than each orchestrator assigning it
    inline, and it is the ONLY function here that moves the secret.
    """
    key, source = resolve(required=True)
    os.environ[KEY_ENV] = key
    return source
