from warnings import warn

from bibtutils.version import __version__


__all__ = ["error", "message"]

from bibtutils.slack import error
from bibtutils.slack import message

warn(
    "This library is deprecated. Please use a supported library: "
    "https://broadinstitute.github.io/bibt-libraries/",
    DeprecationWarning,
)
