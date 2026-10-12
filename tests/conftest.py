from pathlib import Path

import pytest

from sder.methodology import Methodology, load_methodology

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


@pytest.fixture(scope="session")
def methodology() -> Methodology:
    return load_methodology()
