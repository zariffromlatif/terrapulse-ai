"""Cross-Case Scam Intelligence Graph using NetworkX."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Set
import networkx as nx
from proofpath.models import EvidenceItem, SyndicateMatch


class ScamIntelligenceGraph:
    """Maintains a network graph of financial fraud indicators and identifies syndicate clusters."""

    def __init__(self):
        self.graph = nx.Graph()
        self._seed_known_syndicates()

    def _seed_known_syndicates(self):
        """Seed threat intelligence with historical fraud syndicates and indicators."""
        # Syndicate 1: Dhaka bKash Lottery & OTP Phishing Ring
        syn1 = "SYNDICATE-BD-BKASH-RING-01"
        self.graph.add_node(syn1, type="syndicate", label="Dhaka bKash Phishing Ring", severity="CRITICAL")
        known_bd_phones = ["+8801719998877", "+8801822334455", "+8801911223344", "+8801755667788"]
        known_bd_domains = ["bkash-prize-claim.xyz", "bangladeshbank-security-portal.info", "nagad-reward24.live"]
        for p in known_bd_phones:
            self.graph.add_node(p, type="phone", label=p)
            self.graph.add_edge(syn1, p, relation="MEMBER_INDICATOR")
        for d in known_bd_domains:
            self.graph.add_node(d, type="domain", label=d)
            self.graph.add_edge(syn1, d, relation="CONTROLLED_INFRASTRUCTURE")

        # Syndicate 2: Southeast Asia Telegram Task & PayNow Rebate Syndicate
        syn2 = "SYNDICATE-SG-PAYNOW-JOB-RING-02"
        self.graph.add_node(syn2, type="syndicate", label="SG Telegram Task Syndicate", severity="CRITICAL")
        known_sg_phones = ["+6591234567", "+6581239876", "+6598765432"]
        known_sg_handles = ["@recruit_vip_elena", "@task_finance_manager", "@asia_hr_recruiter"]
        known_sg_domains = ["sg-shopee-rebates.top", "lazada-affiliate-portal.vip", "amazon-global-review.site"]
        for p in known_sg_phones:
            self.graph.add_node(p, type="phone", label=p)
            self.graph.add_edge(syn2, p, relation="MEMBER_INDICATOR")
        for h in known_sg_handles:
            self.graph.add_node(h, type="telegram", label=h)
            self.graph.add_edge(syn2, h, relation="OPERATIONAL_HANDLE")
        for d in known_sg_domains:
            self.graph.add_node(d, type="domain", label=d)
            self.graph.add_edge(syn2, d, relation="PHISHING_PORTAL")

        # Historical Case Links for Seed
        hist_case_1 = "HIST-CASE-BD-2025-88"
        self.graph.add_node(hist_case_1, type="case", label="Victim Report (Chittagong)", loss=45000.0)
        self.graph.add_edge(hist_case_1, "+8801719998877", relation="PAID_TO")
        self.graph.add_edge(hist_case_1, "bkash-prize-claim.xyz", relation="VISITED_LINK")

        hist_case_2 = "HIST-CASE-SG-2025-412"
        self.graph.add_node(hist_case_2, type="case", label="Victim Report (Jurong East)", loss=3200.0)
        self.graph.add_edge(hist_case_2, "+6591234567", relation="PAID_TO")
        self.graph.add_edge(hist_case_2, "@recruit_vip_elena", relation="COMMUNICATED_WITH")

    def find_syndicate_matches(self, evidence_items: List[EvidenceItem]) -> List[SyndicateMatch]:
        """Check extracted case entities against known syndicates and connected cases."""
        matched_indicators: Dict[str, List[str]] = {}
        syndicate_scores: Dict[str, float] = {}

        indicators_to_check: Set[str] = set()
        for item in evidence_items:
            for entity in item.extracted_entities:
                if entity.normalized_value:
                    indicators_to_check.add(entity.normalized_value)
                if entity.value:
                    indicators_to_check.add(entity.value)
            for tx in item.extracted_transactions:
                if tx.recipient_account:
                    indicators_to_check.add(tx.recipient_account)
                if tx.recipient:
                    indicators_to_check.add(tx.recipient)

        for ind in indicators_to_check:
            if self.graph.has_node(ind):
                # Check neighbors
                for neighbor in self.graph.neighbors(ind):
                    node_data = self.graph.nodes[neighbor]
                    if node_data.get("type") == "syndicate":
                        syn_id = neighbor
                        if syn_id not in matched_indicators:
                            matched_indicators[syn_id] = []
                        matched_indicators[syn_id].append(ind)
                        syndicate_scores[syn_id] = syndicate_scores.get(syn_id, 0.5) + 0.25

        results: List[SyndicateMatch] = []
        for syn_id, matched in matched_indicators.items():
            syn_node = self.graph.nodes.get(syn_id, {})
            # Count linked cases to this syndicate
            linked_cases = 0
            for neighbor in self.graph.neighbors(syn_id):
                for sub_n in self.graph.neighbors(neighbor):
                    if self.graph.nodes[sub_n].get("type") == "case":
                        linked_cases += 1

            confidence = min(0.98, max(0.70, syndicate_scores.get(syn_id, 0.75)))
            results.append(
                SyndicateMatch(
                    cluster_id=syn_id,
                    known_alias=syn_node.get("label", syn_id),
                    matched_identifiers=list(set(matched)),
                    total_linked_cases=max(1, linked_cases),
                    syndicate_confidence=round(confidence, 2),
                    notes=(
                        f"Direct threat intelligence match: {len(matched)} indicators matched active syndicate infrastructure. "
                        f"Historical incidents indicate coordinated cross-border or multi-victim operations."
                    ),
                )
            )

        return results

    def link_case_to_graph(
        self,
        case_id: str,
        evidence_items: List[EvidenceItem],
        pattern_name: str,
        total_loss: float = 0.0,
    ):
        """Add the analyzed case and its indicators into the live network graph."""
        self.graph.add_node(
            case_id,
            type="case",
            label=f"Case {case_id}",
            pattern=pattern_name,
            loss=total_loss,
        )

        for item in evidence_items:
            for entity in item.extracted_entities:
                val = entity.normalized_value or entity.value
                if not val:
                    continue
                # Add indicator node if not existing
                if not self.graph.has_node(val):
                    self.graph.add_node(val, type=entity.entity_type, label=val)
                # Connect case to indicator
                rel = "PAID_TO" if entity.role == "suspect" and entity.entity_type in ("wallet_account", "bank_account", "phone_number") else "INVOLVED"
                self.graph.add_edge(case_id, val, relation=rel)

            for tx in item.extracted_transactions:
                if tx.recipient_account:
                    rec_acc = tx.recipient_account
                    if not self.graph.has_node(rec_acc):
                        self.graph.add_node(rec_acc, type="account", label=rec_acc)
                    self.graph.add_edge(case_id, rec_acc, relation="TRANSFER_RECIPIENT", amount=tx.amount or 0.0)

    def export_graph_json(self) -> Dict[str, Any]:
        """Export nodes and edges in D3.js / Cytoscape graph format."""
        nodes = []
        for n, data in self.graph.nodes(data=True):
            ntype = data.get("type", "indicator")
            color_map = {
                "syndicate": "#ef4444",    # Red
                "case": "#3b82f6",         # Blue
                "phone": "#f59e0b",        # Amber
                "domain": "#8b5cf6",       # Purple
                "telegram": "#06b6d4",     # Cyan
                "account": "#10b981",      # Emerald
            }
            nodes.append({
                "id": n,
                "label": data.get("label", n),
                "type": ntype,
                "color": color_map.get(ntype, "#6b7280"),
                "degree": self.graph.degree(n),
                "metadata": {k: v for k, v in data.items() if k not in ("label", "type")},
            })

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relation": data.get("relation", "LINKED"),
                "metadata": {k: v for k, v in data.items() if k != "relation"},
            })

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
        }
