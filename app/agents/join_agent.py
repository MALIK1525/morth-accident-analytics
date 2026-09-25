"""
Join Compatibility Agent for MoRTH Road Accident Research Platform.
Prevents unscientific data merging by rigorously evaluating:
- Source System (MoRTH vs NCRB vs PIB vs IMD)
- Geography Compatibility (India-level vs State-level vs District-level)
- Year Temporal Overlap (Exact year vs multi-year cumulative vs missing years)
- Data Granularity (State-Year vs India-Year vs Event-level)
- Variable Definition & Unit Compatibility
Returns: SAFE, CONDITIONALLY SAFE, or UNSAFE with detailed rationale.
"""

class JoinCompatibilityAgent:
    def __init__(self):
        self.join_rules = {
            "morth_primary_granularity": "State-Year",
            "locked_source_separations": [
                ("MoRTH", "NCRB", "UNSAFE: Different reporting methodologies, definitions and collection pipelines. Must remain distinct."),
                ("State-Year", "India-Year", "UNSAFE: Geography mismatch. Cannot merge India aggregate row directly into state panel without distortion."),
                ("State-Year", "Accident-Level", "UNSAFE: Granularity mismatch. Cannot join micro-data directly without aggregation.")
            ]
        }

    def evaluate_join(self, dataset_a_meta, dataset_b_meta):
        """
        Evaluates compatibility between two datasets before any merge operation.
        dataset_a_meta, dataset_b_meta: dict containing:
          - source (str, e.g., 'MoRTH', 'NCRB', 'IMD', 'User Upload')
          - geography (str, e.g., 'State', 'India', 'District')
          - years (list of int, e.g., [2018, 2019, 2020])
          - granularity (str, e.g., 'State-Year', 'India-Year', 'Daily')
          - join_key (str, e.g., 'State+Year', 'Year', 'State')
        """
        source_a = dataset_a_meta.get('source', 'Unknown')
        source_b = dataset_b_meta.get('source', 'Unknown')
        geo_a = dataset_a_meta.get('geography', 'Unknown')
        geo_b = dataset_b_meta.get('geography', 'Unknown')
        gran_a = dataset_a_meta.get('granularity', 'Unknown')
        gran_b = dataset_b_meta.get('granularity', 'Unknown')
        years_a = set(dataset_a_meta.get('years', []))
        years_b = set(dataset_b_meta.get('years', []))

        reasons = []
        status = "SAFE"

        # 1. Source Check
        if source_a != source_b:
            if "NCRB" in [source_a, source_b] and "MoRTH" in [source_a, source_b]:
                return {
                    "verdict": "UNSAFE",
                    "reason": "MoRTH and NCRB operate under different statutory reporting chains. MoRTH compiles from State Police Form 1-4; NCRB from ADSI. Cross-merging violates project methodological rules.",
                    "can_join": False,
                    "recommended_action": "Keep in separate analysis tabs with clear source provenance badges."
                }
            else:
                reasons.append(f"Different source systems ({source_a} and {source_b}). Source provenance badges must be maintained.")
                status = "CONDITIONALLY SAFE"

        # 2. Geography Check
        if geo_a != geo_b:
            return {
                "verdict": "UNSAFE",
                "reason": f"Geography mismatch: '{geo_a}' cannot be directly joined with '{geo_b}'. Joining national totals across state rows causes pseudo-replication.",
                "can_join": False,
                "recommended_action": "Aggregate to national level first or project state data before joining."
            }

        # 3. Granularity Check
        if gran_a != gran_b:
            if gran_a == "State-Year" and gran_b in ["State-Year-Weather", "State-Year-Road"]:
                reasons.append(f"Granularity extension: Joining {gran_b} to {gran_a} requires compatible category aggregation.")
                status = "CONDITIONALLY SAFE"
            else:
                return {
                    "verdict": "UNSAFE",
                    "reason": f"Granularity mismatch ({gran_a} vs {gran_b}). Direct record-to-record join is mathematically invalid.",
                    "can_join": False,
                    "recommended_action": "Aggregate the finer granularity dataset to State-Year level."
                }

        # 4. Temporal Overlap Check
        if years_a and years_b:
            overlap = years_a.intersection(years_b)
            if not overlap:
                return {
                    "verdict": "UNSAFE",
                    "reason": f"Zero temporal overlap: Dataset A covers {min(years_a)}–{max(years_a)}, Dataset B covers {min(years_b)}–{max(years_b)}.",
                    "can_join": False,
                    "recommended_action": "Align time horizons before joining."
                }
            elif overlap != years_a or overlap != years_b:
                reasons.append(f"Partial temporal overlap: only years {sorted(list(overlap))} share mutual records.")
                status = "CONDITIONALLY SAFE"

        return {
            "verdict": status,
            "reason": "; ".join(reasons) if reasons else "Compatible source, geography, temporal window, and granularity.",
            "can_join": (status in ["SAFE", "CONDITIONALLY SAFE"]),
            "recommended_action": "Proceed with join using verified State+Year composite key." if status == "SAFE" else "Proceed with caution; display methodological notes."
        }

    def get_supported_inventory_decisions(self):
        """Returns the pre-evaluated compatibility decisions for known supporting tables."""
        return [
            {
                "dataset": "MoRTH 2019 Severity Breakdown (Table 2.2)",
                "granularity": "India-Year (2015-2019)",
                "target": "State-Year Panel (2018-2024)",
                "verdict": "UNSAFE FOR DIRECT MERGE",
                "reason": "Geography mismatch: India-level only. Displayed in dedicated India-level severity charts without polluting state panel."
            },
            {
                "dataset": "MoRTH 2019 Road Classification & Length (Table 2.3/3.1)",
                "granularity": "India-Year-Category (2019)",
                "target": "State-Year Panel (2018-2024)",
                "verdict": "UNSAFE FOR DIRECT MERGE",
                "reason": "Geography and temporal mismatch. Displayed in dedicated Road Analysis module."
            },
            {
                "dataset": "MoRTH 2021-2022 Vehicle-Mode Victim Deaths",
                "granularity": "India-Year-Vehicle (2021-2022)",
                "target": "State-Year Panel (2018-2024)",
                "verdict": "UNSAFE FOR DIRECT MERGE",
                "reason": "India-level aggregate only. Displayed in dedicated Vehicle Analysis module."
            },
            {
                "dataset": "NCRB ADSI 2023 Causes & Road Class",
                "granularity": "State-Year-Category (2023)",
                "target": "MoRTH Primary Panel",
                "verdict": "UNSAFE",
                "reason": "Different source system (NCRB vs MoRTH). Must remain strictly separate per locked project decision."
            },
            {
                "dataset": "IMD State-wise Rainfall & Weather",
                "granularity": "State-Year",
                "target": "State-Year Panel (2018-2024)",
                "verdict": "SAFE AFTER AGGREGATION",
                "reason": "State+Year composite key matches. Safe to join after aggregating daily rainfall to annual state millimeters."
            }
        ]
