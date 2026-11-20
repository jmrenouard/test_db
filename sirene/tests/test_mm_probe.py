"""Unit and optional live 2-node integration tests for multi-master qualification."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from sirene_etl.mm_probe import (
    ProbeResult,
    Scorecard,
    classify_verdict,
    format_scorecard_markdown,
    run_mm_qualification,
    scorecard_to_dict,
    setup_native_birep,
)

EXPECTED_PROBE_IDS: tuple[str, ...] = (
    "P1_DDL_COMPAT",
    "P2_SEQUENCE_SPLIT_BRAIN",
    "P3_CONCURRENT_SIRET_UPSERT",
    "P4_CROSS_NODE_FK_CAUSALITY",
    "P5_BULK_COPY_REPLICATION_LAG",
)

VALID_STATUSES = frozenset({"PASS", "WARN", "FAIL"})
VALID_VERDICTS = frozenset(
    {
        "PRODUCTION_MULTI_MASTER_READY",
        "CONDITIONAL_PARTITIONED_WRITES_ONLY",
        "INCOMPATIBLE_WITH_SIRENE_3NF",
    }
)


def _sample_probes(statuses: tuple[str, ...]) -> list[ProbeResult]:
    return [
        ProbeResult(
            probe_id=probe_id,
            name=f"Probe {probe_id}",
            status=status,
            latency_ms=12.34,
            detail=f"Sample outcome {status} for {probe_id}",
            metrics={"sample": idx + 1},
        )
        for idx, (probe_id, status) in enumerate(zip(EXPECTED_PROBE_IDS, statuses))
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("statuses", "expected_verdict"),
    [
        (
            ("PASS", "PASS", "PASS", "PASS", "PASS"),
            "PRODUCTION_MULTI_MASTER_READY",
        ),
        (
            ("WARN", "PASS", "WARN", "PASS", "PASS"),
            "CONDITIONAL_PARTITIONED_WRITES_ONLY",
        ),
        (
            ("PASS", "FAIL", "WARN", "PASS", "PASS"),
            "INCOMPATIBLE_WITH_SIRENE_3NF",
        ),
    ],
)
def test_scorecard_verdicts_and_serialization(
    statuses: tuple[str, ...],
    expected_verdict: str,
) -> None:
    """Verify classify_verdict, Scorecard serialization, and JSON export."""
    probes = _sample_probes(statuses)
    verdict = classify_verdict(probes)
    assert verdict == expected_verdict

    scorecard = Scorecard(
        candidate="pg18-test-candidate",
        pg_version_a="18.0",
        pg_version_b="18.0",
        verdict=verdict,
        probes=probes,
    )
    assert scorecard.verdict in VALID_VERDICTS
    assert classify_verdict([]) == "INCOMPATIBLE_WITH_SIRENE_3NF"

    payload = scorecard_to_dict(scorecard)
    assert payload["candidate"] == "pg18-test-candidate"
    assert payload["pg_version_a"] == "18.0"
    assert payload["pg_version_b"] == "18.0"
    assert payload["verdict"] == expected_verdict
    assert len(payload["probes"]) == 5
    assert [p["probe_id"] for p in payload["probes"]] == list(EXPECTED_PROBE_IDS)

    serialized = json.dumps(payload)
    assert expected_verdict in serialized


@pytest.mark.unit
def test_format_scorecard_markdown_renders_all_probes() -> None:
    """Verify Markdown report includes candidate, versions, verdict, and all 5 probes."""
    scorecard = Scorecard(
        candidate="pg18-native-birep",
        pg_version_a="18.0 (Debian)",
        pg_version_b="18.0 (Debian)",
        verdict="CONDITIONAL_PARTITIONED_WRITES_ONLY",
        probes=_sample_probes(("WARN", "PASS", "WARN", "WARN", "PASS")),
    )
    markdown = format_scorecard_markdown(scorecard)
    assert "pg18-native-birep" in markdown
    assert "CONDITIONAL_PARTITIONED_WRITES_ONLY" in markdown
    for probe_id in EXPECTED_PROBE_IDS:
        assert probe_id in markdown
    assert "WARN" in markdown
    assert "PASS" in markdown


@pytest.mark.unit
def test_mm_probe_has_ponytail_shortcut_comment(sirene_dir: Path) -> None:
    """Verify mm_probe.py documents its deliberate 2-node Ponytail shortcut ceiling."""
    mm_probe_src = sirene_dir / "src" / "sirene_etl" / "mm_probe.py"
    assert mm_probe_src.is_file(), f"Missing {mm_probe_src}"
    content = mm_probe_src.read_text(encoding="utf-8")
    assert "shortcut:" in content, "Expected Ponytail 'shortcut:' comment in mm_probe.py"


@pytest.mark.integration
@pytest.mark.skipif(
    not (os.environ.get("MM_DSN_A") and os.environ.get("MM_DSN_B")),
    reason="MM_DSN_A and MM_DSN_B env vars required for live 2-node MM qualification",
)
def test_live_two_node_pg18_mm_qualification() -> None:
    """Run native PG 18 bidirectional setup and all 5 qualification probes on 2 live nodes."""
    dsn_a = os.environ["MM_DSN_A"]
    dsn_b = os.environ["MM_DSN_B"]
    internal_dsn_a = os.environ.get("MM_INTERNAL_DSN_A") or dsn_a
    internal_dsn_b = os.environ.get("MM_INTERNAL_DSN_B") or dsn_b

    setup_native_birep(
        dsn_a,
        dsn_b,
        internal_dsn_a,
        internal_dsn_b,
        stagger_sequences=True,
    )
    scorecard = run_mm_qualification(
        dsn_a,
        dsn_b,
        candidate_name="pg18-native-birep",
        batch_rows=50,
        timeout_sec=15.0,
    )

    assert scorecard.verdict in VALID_VERDICTS
    probe_ids = [probe.probe_id for probe in scorecard.probes]
    assert probe_ids == list(EXPECTED_PROBE_IDS)
    for probe in scorecard.probes:
        assert probe.status in VALID_STATUSES
        assert probe.latency_ms >= 0.0
        assert probe.detail.strip()
        assert isinstance(probe.metrics, dict)

    markdown = format_scorecard_markdown(scorecard)
    assert scorecard.verdict in markdown
    payload = scorecard_to_dict(scorecard)
    assert len(payload["probes"]) == 5
