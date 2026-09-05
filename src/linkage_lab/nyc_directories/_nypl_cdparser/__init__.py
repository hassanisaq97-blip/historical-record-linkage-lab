"""Vendored copy of NYPL's city-directory-entry-parser (MIT licensed).

Source: https://github.com/nypl-spacetime/city-directory-entry-parser
Commit: cb695a94a4d4ef57561a77f62f518d773321fe6d
Author: Stephen Balogh <sgb334@nyu.edu>

Vendored (rather than installed from PyPI, where it is not published) so
that this project's real-world case study can reuse NYPL's own published
parsing tool instead of writing a bespoke parser from scratch. Only the
import paths were changed (absolute `cdparser.X` -> relative `.X`) to fit
this package's namespace; the parsing logic itself is untouched.
"""

from . import Classifier
from . import Utils
from . import LabeledEntry
from . import Features
