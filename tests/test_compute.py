"""
Regression test for: q2_shared_asv.compute.compute

* Covers boundary values for `percentage` (0.0, 0.5, 1.0)
* Covers both branches of the conditional: shared ASVs > 0 and == 0
* Achieves 100% C0 (statement) coverage
"""

import pytest
import importlib
import sys
import pathlib


# Add the project root to sys.path so we can import q2_shared_asv
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# Load the compute function from the plugin module
compute_mod = importlib.import_module("q2_shared_asv.compute")
compute = compute_mod.compute


# FakeTable mimics biom.Table (only shape and copy are needed)
class FakeTable:
    def __init__(self, rows: int, cols: int):
        self._shape = (rows, cols)

    @property
    def shape(self):
        return self._shape

    def copy(self):
        return FakeTable(*self._shape)

    def __repr__(self):
        r, c = self._shape
        return f"<FakeTable {r}x{c}>"


# Monkeypatch q2-feature-table functions
def _patch_q2(monkeypatch, *, merged_shape, cond_shape, empty_shape):
    """
    Replace q2-feature-table functions with stubs:
    - filter_samples            -> returns 2x1 table
    - merge                     -> returns merged_shape table
    - filter_features_cond.     -> returns cond_shape table
    - filter_features           -> returns empty_shape table
    """
    monkeypatch.setattr(
        compute_mod,
        "filter_samples",
        lambda *a, **kw: FakeTable(2, 1),
        raising=True,
    )

    monkeypatch.setattr(
        compute_mod,
        "merge",
        lambda *a, **kw: FakeTable(*merged_shape),
        raising=True,
    )

    monkeypatch.setattr(
        compute_mod,
        "filter_features_conditionally",
        lambda *a, **kw: FakeTable(*cond_shape),
        raising=True,
    )

    monkeypatch.setattr(
        compute_mod,
        "filter_features",
        lambda *a, **kw: FakeTable(*empty_shape),
        raising=True,
    )


# Test: shared ASVs > 0 → goes through the `else` branch
@pytest.mark.parametrize("percentage", [0.0, 0.5, 1.0])
def test_compute_non_empty(monkeypatch, percentage):
    _patch_q2(
        monkeypatch,
        merged_shape=(3, 2),
        cond_shape=(2, 2),      # 2 rows → else branch
        empty_shape=(0, 1),
    )

    result = compute(
        table=FakeTable(5, 3),
        sample_a="A",
        sample_b="B",
        metadata=None,
        percentage=percentage,
    )

    assert isinstance(result, FakeTable)
    assert result.shape == (2, 2)


# Test: shared ASVs == 0 → goes through the `if` branch
def test_compute_empty(monkeypatch):
    _patch_q2(
        monkeypatch,
        merged_shape=(3, 2),
        cond_shape=(0, 2),     # 0 rows → if branch
        empty_shape=(0, 1),    # returned table
    )

    result = compute(
        table=FakeTable(4, 3),
        sample_a="A",
        sample_b="B",
        metadata=None,
        percentage=0.5,
    )

    assert result.shape == (0, 1)
