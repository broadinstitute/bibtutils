"""A Python package featuring functionality often used by BITS Blue Team (BIBT)."""
from warnings import warn

from bibtutils.version import __version__

warn(
    "This library is deprecated. Please use a supported library: "
    "https://broadinstitute.github.io/bibt-libraries/",
    DeprecationWarning,
)

__all__ = ["gcp", "slack"]

from bibtutils import gcp
from bibtutils import slack

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
