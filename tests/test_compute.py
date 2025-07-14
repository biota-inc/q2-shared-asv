"""
Regression test for: q2_shared_asv.compute.compute

* Boundary values for `percentage` (0.0, 0.5, 1.0)
* Both branches of the conditional (shared ASVs > 0 and == 0)
"""

import pytest
import importlib
import sys
import pathlib


# ---------------------------------------------------------------------------
# Project import path
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

compute_mod = importlib.import_module("q2_shared_asv.compute")
compute = compute_mod.compute


# ---------------------------------------------------------------------------
# Minimal biom.Table stub with payload support
class FakeTable:
    """
    Light-weight substitute for biom.Table used exclusively for unit tests.
    """

    def __init__(self, rows: int, cols: int, *, name: str, payload=None):
        self._shape = (rows, cols)
        self.name = name
        # payload can be any hashable object – we just propagate it
        self.payload = payload

    # biom.Table API subset --------------------------------------------------
    @property
    def shape(self):
        return self._shape

    def copy(self):
        # copy should duplicate payload to emulate real biom.Table.copy()
        return FakeTable(
            *self._shape,
            name=f"{self.name}_copy",
            payload=self.payload,
        )

    # For readable assert failure messages
    def __repr__(self):
        r, c = self._shape
        return f"<FakeTable {r}x{c} {self.name}>"

    # Optional equality based on shape & payload (not required, but handy)
    def __eq__(self, other):
        return (
            isinstance(other, FakeTable)
            and self._shape == other._shape
            and self.payload == other.payload
            and self.name == other.name
        )


# ---------------------------------------------------------------------------
# Helper to monkey-patch q2-feature-table API
def _patch_q2(monkeypatch, *, merged_tbl, cond_tbl, empty_tbl):
    """
    Patch q2_feature_table functions so they return **specific** FakeTable
    instances supplied by the caller. This allows identity assertions.
    """

    # Each sample filter returns a fresh 2x1 table; its payload is irrelevant
    monkeypatch.setattr(
        compute_mod,
        "filter_samples",
        lambda *_, **__: FakeTable(2, 1, name="filtered_sample"),
        raising=True,
    )

    # merge() returns the caller-provided merged_tbl
    monkeypatch.setattr(
        compute_mod,
        "merge",
        lambda *_, **__: merged_tbl,
        raising=True,
    )

    # filter_features_conditionally() returns cond_tbl
    monkeypatch.setattr(
        compute_mod,
        "filter_features_conditionally",
        lambda *_, **__: cond_tbl,
        raising=True,
    )

    # filter_features() returns empty_tbl (used when cond_tbl.shape[0] == 0)
    monkeypatch.setattr(
        compute_mod,
        "filter_features",
        lambda *_, **__: empty_tbl,
        raising=True,
    )


# ============================================================================
# branch: shared ASVs > 0  (else)
# ============================================================================
@pytest.mark.parametrize("percentage", [0.0, 0.5, 1.0])
def test_compute_non_empty(monkeypatch, percentage):
    merged_tbl = FakeTable(3, 2, name="merged", payload="M")
    cond_tbl = FakeTable(2, 2, name="cond_non_empty", payload="C")
    empty_tbl = FakeTable(0, 1, name="empty_unused")

    _patch_q2(
        monkeypatch,
        merged_tbl=merged_tbl,
        cond_tbl=cond_tbl,
        empty_tbl=empty_tbl,
    )

    result = compute(
        table=FakeTable(5, 3, name="input"),
        sample_a="A",
        sample_b="B",
        metadata=None,
        percentage=percentage,
    )

    # Identity & content checks
    assert result is cond_tbl
    assert result.payload == "C"
    assert result.shape == (2, 2)


# ============================================================================
# branch: shared ASVs == 0  (if)
# ============================================================================
def test_compute_empty(monkeypatch):
    merged_tbl = FakeTable(3, 2, name="merged", payload="M")
    cond_tbl = FakeTable(0, 2, name="cond_empty", payload="C")      # 0 rows
    empty_tbl = FakeTable(0, 1, name="empty_returned", payload="E")

    _patch_q2(
        monkeypatch,
        merged_tbl=merged_tbl,
        cond_tbl=cond_tbl,
        empty_tbl=empty_tbl,
    )

    result = compute(
        table=FakeTable(4, 3, name="input"),
        sample_a="A",
        sample_b="B",
        metadata=None,
        percentage=0.5,
    )

    # Should return the exact empty_tbl object
    assert result is empty_tbl
    assert result.payload == "E"
    assert result.shape == (0, 1)
