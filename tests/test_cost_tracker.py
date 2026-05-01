"""Tests for mini_agent.research.models.cost_tracker."""

from __future__ import annotations

import pytest

from mini_agent.research.models.cost_tracker import CostEntry, CostTracker


@pytest.fixture
def tracker(tmp_path):
    return CostTracker(workspace_path=tmp_path)


class TestEntry:
    def test_auto_timestamp(self):
        assert CostEntry(model="gpt-4o", input_tokens=100, output_tokens=50).timestamp != ""

    def test_fields(self):
        e = CostEntry(
            model="gpt-4o",
            provider="openai",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.0075,
            task_type="writing",
        )
        assert e.model == "gpt-4o" and e.task_type == "writing"


class TestRecord:
    def test_adds(self, tracker):
        assert isinstance(
            tracker.record(model="gpt-4o", provider="openai", input_tokens=1000, output_tokens=500), CostEntry
        )
        assert tracker.count == 1

    def test_calculates_cost(self, tracker):
        assert tracker.record(
            model="gpt-4o", provider="openai", input_tokens=1_000_000, output_tokens=0
        ).cost_usd == pytest.approx(2.5, abs=0.01)

    def test_multiple(self, tracker):
        tracker.record(model="gpt-4o", provider="openai", input_tokens=100, output_tokens=50)
        tracker.record(model="gpt-4o-mini", provider="openai", input_tokens=200, output_tokens=100)
        assert tracker.count == 2


class TestTotalCost:
    def test_zero(self, tracker):
        assert tracker.get_total_cost() == 0.0

    def test_sums(self, tracker):
        tracker.record(model="gpt-4o", provider="openai", input_tokens=1_000_000, output_tokens=0)
        tracker.record(model="gpt-4o", provider="openai", input_tokens=0, output_tokens=1_000_000)
        assert tracker.get_total_cost() == pytest.approx(12.5, abs=0.01)


class TestByPhase:
    def test_groups(self, tracker):
        tracker.record(model="gpt-4o", provider="openai", input_tokens=1000, output_tokens=0, task_type="planning")
        tracker.record(model="gpt-4o", provider="openai", input_tokens=1000, output_tokens=0, task_type="writing")
        assert "planning" in tracker.get_cost_by_phase() and "writing" in tracker.get_cost_by_phase()


class TestByModel:
    def test_groups(self, tracker):
        tracker.record(model="gpt-4o", provider="openai", input_tokens=1000, output_tokens=0)
        tracker.record(model="gpt-4o-mini", provider="openai", input_tokens=1000, output_tokens=0)
        assert "gpt-4o" in tracker.get_cost_by_model() and "gpt-4o-mini" in tracker.get_cost_by_model()


class TestPersistence:
    def test_save_load(self, tmp_path):
        t = CostTracker(workspace_path=tmp_path)
        t.record(model="gpt-4o", provider="openai", input_tokens=500, output_tokens=200)
        t.save()
        assert CostTracker(workspace_path=tmp_path).count == 1

    def test_empty(self, tmp_path):
        assert CostTracker(workspace_path=tmp_path).count == 0


class TestBudget:
    def test_not_over(self, tracker):
        assert tracker.is_over_budget is False

    def test_remaining(self, tracker):
        assert tracker.remaining_budget == pytest.approx(50.0, abs=0.01)


class TestSummary:
    def test_has_total(self, tracker):
        tracker.record(model="gpt-4o", provider="openai", input_tokens=1000, output_tokens=500)
        assert "Total cost" in tracker.get_summary()

    def test_empty(self, tracker):
        assert "Total cost: $0.0000" in tracker.get_summary()
