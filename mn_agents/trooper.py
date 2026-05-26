"""
mn_agents/trooper.py
Minnesota State Patrol Trooper — the street-level actor.

Lipsky (1980): street-level bureaucrats exercise substantial discretion
because supervisors cannot monitor every encounter. The trooper is the
point where institutional policy meets physical reality.

Key insight: the trooper's deployment location is NOT a management decision —
it is an output of seniority bidding under the MELS contract. Senior troopers
claim the safest, most predictable, lowest-stress posts. Junior troopers get
what's left. Citation density reflects this sorting, not optimal enforcement.
"""

from dataclasses import dataclass, field
from typing import Optional
from .base import Institution, InstitutionType, Budget, Edge, EdgeType


@dataclass
class StopConditions:
    """Physical prerequisites for a lawful traffic stop."""
    safe_shoulder:    bool   # paved shoulder wide enough to pull over safely
    approach_safe:    bool   # can officer approach driver-side without traffic exposure
    jurisdiction:     bool   # MSP has authority here (not MPD/Sheriff/MAC/Metro)
    equipment_ready:  bool   # radar/LIDAR operational and calibrated
    shift_active:     bool   # stop initiated with enough shift time to complete it

    @property
    def can_stop(self) -> bool:
        return all([
            self.safe_shoulder,
            self.approach_safe,
            self.jurisdiction,
            self.equipment_ready,
            self.shift_active,
        ])


@dataclass
class Trooper(Institution):

    seniority_rank: int   = 5    # 1=most senior at post; affects shift/zone assignment
    shift:          str   = "days"  # days | evenings | nights — bid by seniority
    assigned_zone:  str   = "I-94 Metro"

    def __post_init__(self):
        self.id          = "trooper"
        self.name        = "MSP Trooper"
        self.type        = InstitutionType.MSP
        self.budget      = Budget(appropriated=95_000)   # fully-loaded cost per trooper ~$95k
        self.headcount   = 1
        self.jurisdiction = "MN state highways and interstates"
        self.objective   = (
            "Maximize legitimate stops per shift; minimize personal safety risk; "
            "preserve seniority standing; avoid discipline."
        )
        self.constraints = [
            "MELS CBA: shift assignment via seniority bid — cannot be overridden by management",
            "MELS CBA: minimum rest between shifts (fatigue constraint on coverage)",
            "Road geometry: stop requires usable shoulder (enforcement shadow on no-shoulder segments)",
            "Approach safety: driver-side approach on divided highway exposes trooper to live traffic",
            "Jurisdiction: MSP authority ends at city limits / county roads (seam creates coverage gaps)",
            "Equipment: radar/LIDAR allocated at post level, not per trooper",
            "Shift end: stops initiated near shift change may not complete — troopers avoid late stops",
            "District Court behavior: contested citations in lenient districts reduce stop value",
        ]
        self.edges = [
            Edge("post_commander", EdgeType.CONSTRAINED_BY, 3, "Takes daily deployment orders"),
            Edge("mels",           EdgeType.CONSTRAINED_BY, 3, "CBA governs every operational parameter"),
            Edge("driver",         EdgeType.ADVERSARIAL,    3, "Primary interaction point"),
            Edge("dist_court",     EdgeType.CONSTRAINED_BY, 2, "Dismissal rate shapes stop calculus"),
        ]
        self.notes = (
            "The trooper's effective deployment is the joint output of: "
            "(1) which zone seniority let them bid, "
            "(2) which road segments in that zone have safe shoulders, "
            "(3) what equipment is available at their post. "
            "Management cannot place a specific trooper at a specific location without union challenge. "
            "This is the primary explanation for persistent enforcement shadows."
        )

    def evaluate_stop(self, conditions: StopConditions, violation_mph_over: int) -> dict:
        """
        Decide whether to initiate a stop given physical conditions and violation severity.
        Returns decision with reasoning.
        """
        if not conditions.can_stop:
            blocking = [k for k, v in conditions.__dict__.items() if not v]
            return {
                "decision": "no_stop",
                "reason": f"Blocking conditions: {blocking}",
                "enforcement_shadow": True,
            }

        # Low violation + late in shift = warn or skip
        if violation_mph_over < 15 and not conditions.shift_active:
            return {
                "decision": "no_stop",
                "reason": "Sub-threshold violation near shift end — not worth the overtime risk",
                "enforcement_shadow": False,
            }

        if violation_mph_over >= 20:
            return {"decision": "stop_and_cite", "reason": "Clear violation, safe conditions"}

        if violation_mph_over >= 10:
            return {"decision": "stop_discretionary", "reason": "Moderate violation — trooper discretion"}

        return {"decision": "warning_or_skip", "reason": "Minor violation"}

    def respond_to(self, pressure: dict) -> dict:
        ptype = pressure.get("type")

        if ptype == "budget_cut":
            return {
                "response": "no_direct_effect",
                "note": (
                    "Trooper salary is protected by MELS contract. Budget cuts hit "
                    "equipment (fewer radar units), overtime (less coverage), and "
                    "training — not the trooper's base deployment."
                )
            }

        if ptype == "quota_pressure":
            return {
                "response": "increased_stops_on_safe_segments",
                "note": (
                    "Troopers respond to quota pressure by maximizing stops on "
                    "predictable safe-shoulder segments. This concentrates citations "
                    "further on already-visible corridors."
                )
            }

        if ptype == "media_scrutiny":
            return {
                "response": "reduced_discretionary_stops",
                "note": (
                    "Under scrutiny, troopers shift toward clear-cut violations only. "
                    "Discretionary stops (10-15 mph over) decline. Documentation increases."
                )
            }

        return {"response": "no_change", "note": f"Pressure type '{ptype}' not recognized"}
