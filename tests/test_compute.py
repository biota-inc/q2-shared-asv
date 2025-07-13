"""
回帰テスト: q2_shared_asv.compute.compute

* percentage の境界値 (0, 0.5, 1) を網羅
* if/else（共有 ASV 0 行かどうか）の両ブランチを網羅
* C0 カバレッジ 100 %
"""
import pytest
import importlib
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

#--- テスト対象モジュールを読み込み ------------------------
compute_mod = importlib.import_module("q2_shared_asv.compute")
compute = compute_mod.compute

#--- biom.Table もどき ------------------------------------
class FakeTable:
    """shape と copy() だけを持つ軽量オブジェクト"""
    def __init__(self, rows: int, cols: int):
        self._shape = (rows, cols)

    @property
    def shape(self):
        return self._shape

    def copy(self):
        return FakeTable(*self._shape)

    # デバッグ用
    def __repr__(self):
        r, c = self._shape
        return f"<FakeTable {r}x{c}>"

#--- 共通ヘルパ: q2_feature_table の関数をモンキーパッチ -------
def _patch_q2(monkeypatch, *, merged_shape, cond_shape, empty_shape):
    """
    ・filter_samples          → 常に 1 列テーブルを返す
    ・merge                   → merged_shape のテーブル
    ・filter_features_cond.   → cond_shape のテーブル
    ・filter_features         → empty_shape のテーブル
    """

    monkeypatch.setattr(
        compute_mod,
        "filter_samples",
        lambda *a, **kw: FakeTable(2, 1),  # rows, cols
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

# =================================================================
# 共有 ASV が 1 行以上 → else ブランチ
# =================================================================
@pytest.mark.parametrize("percentage", [0.0, 0.5, 1.0])
def test_compute_non_empty(monkeypatch, percentage):
    _patch_q2(
        monkeypatch,
        merged_shape=(3, 2),   # dummy
        cond_shape=(2, 2),     # > 0 行 → else
        empty_shape=(0, 1),    # unused
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

# =================================================================
# 共有 ASV が 0 行 → if ブランチ
# =================================================================
def test_compute_empty(monkeypatch):
    _patch_q2(
        monkeypatch,
        merged_shape=(3, 2),
        cond_shape=(0, 2),     # 0 行 → if
        empty_shape=(0, 1),    # 返ってくるテーブル
    )

    result = compute(
        table=FakeTable(4, 3),
        sample_a="A",
        sample_b="B",
        metadata=None,
        percentage=0.5,
    )

    assert result.shape == (0, 1)
