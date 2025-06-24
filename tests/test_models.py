# ==================== tests/test_models.py ================
import pytest
from stdsync.core.models import Standard

def test_standard():
    s = Standard("GB/T 1—2024", "示例", None)
    assert "GB/T" in s.code