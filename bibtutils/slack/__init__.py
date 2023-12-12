from warnings import warn

from bibtutils.version import __version__

warn(
    "This library is deprecated. Please use a supported library: "
    "https://broadinstitute.github.io/bibt-libraries/",
    DeprecationWarning,
)

__all__ = ["error", "message"]

from bibtutils.slack import error
from bibtutils.slack import message
