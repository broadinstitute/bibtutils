from warnings import warn

from bibtutils.version import __version__

__all__ = ["storage", "bigquery", "secrets", "pubsub"]

from bibtutils.gcp import storage
from bibtutils.gcp import secrets
from bibtutils.gcp import pubsub
from bibtutils.gcp import bigquery

warn(
    "This library is deprecated. Please use a supported library: "
    "https://broadinstitute.github.io/bibt-libraries/",
    DeprecationWarning,
)
