import pytest

import re

@pytest.fixture(scope='module')
def FUNCC_DECLARATION() -> str:
    """
    FUNCC: a very functional func (inspired by the vernacular "thicc")
    """
    return 'def FUNCC({sig}): return'


