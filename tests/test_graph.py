"""Unit tests for Scam Intelligence Graph and Syndicate Matching."""

import pytest
from proofpath.extractor import EvidenceExtractor
from proofpath.graph import ScamIntelligenceGraph


def test_graph_seed_and_syndicate_match():
    graph = ScamIntelligenceGraph()
    extractor = EvidenceExtractor()

    # Evidence with known seeded phone number +8801719998877
    item = extractor.process_file_content(
        "evidence.txt",
        b"Victim transferred BDT 25000 to +8801719998877 and visited bkash-prize-claim.xyz",
        "text/plain",
    )

    matches = graph.find_syndicate_matches([item])
    assert len(matches) >= 1
    assert matches[0].cluster_id == "SYNDICATE-BD-BKASH-RING-01"
    assert "+8801719998877" in matches[0].matched_identifiers
    assert matches[0].syndicate_confidence >= 0.70


def test_graph_export_and_link():
    graph = ScamIntelligenceGraph()
    extractor = EvidenceExtractor()

    item = extractor.process_file_content(
        "evidence_sg.txt",
        b"PayNow to +6591234567 amount SGD 1500",
        "text/plain",
    )

    graph.link_case_to_graph("CASE-TEST-001", [item], "Task Scam", 1500.0)
    data = graph.export_graph_json()

    assert data["node_count"] > 5
    assert data["edge_count"] > 5
    case_nodes = [n for n in data["nodes"] if n["id"] == "CASE-TEST-001"]
    assert len(case_nodes) == 1
