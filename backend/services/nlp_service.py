import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ml.api.nlp_interface import (
    analyze_contract
)


def analyze_text(text):

    return analyze_contract(text)