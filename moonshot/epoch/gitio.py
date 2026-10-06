"""Git objects written directly from bytes, and remote operations with classified errors (CONTRACT s3)."""


class GitError(Exception):
    """A git operation failed."""


class RemoteUnavailable(GitError):
    """The remote could not be reached; nothing is known to have changed there."""


class AmbiguousPush(GitError):
    """A push gave no definitive answer; it may or may not have applied (CONTRACT s4)."""


class AuthError(GitError):
    """The remote refused the credential."""


class RateLimited(GitError):
    """The remote throttled us (a T004 stop condition)."""


class ForbiddenRef(GitError):
    """A ref outside refs/moonshot/<namespace>/ (CONTRACT s3)."""


class ForbiddenRemote(GitError):
    """A remote on the denylist, e.g. the Prometheus repository (OP-LC1 #1)."""
