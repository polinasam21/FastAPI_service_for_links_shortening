import pytest
from app.main import generate_link_short_code

def test_generate_short_code_length():
    short_code = generate_link_short_code()
    assert len(short_code) == 6

