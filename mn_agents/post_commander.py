"""
mn_agents/post_commander.py
MSP Post Commander — the practical deployment decision-maker.

The post commander is where agency policy meets local reality.
They cannot override the MELS contract (seniority bidding determines
who works which shift and zone), but they control equipment assignment,
daily tasking emphasis, and tactical response to incidents.

This is the most important layer for understanding actual citation patterns.
The Commissioner sets strategy; the Post Commander sets reality.
"""

from dataclasses import dataclass, field
from typing import Optional
from .base import Institution, InstitutionType, Budget, Edge, EdgeType


@dataclass
class PostCommander(Institution):

    post_name:          str  = "Metro District"
    troopers_assigned:  int  = 40    # typical metro post
    shifts:             int  = 3     # days / evenings / nights
    radar_units:        int  = 15    # shared pool across troopers

    def __post_init__(self):
        self.id          = "post_commander"
        self.name        = "MSP Post Commander"
        self.type        = InstitutionType.MSP
        self.budget      = Budget(appropriated=4_000_000)  # post operating budget
        self.headcount   = self.troopers_assigned
        self.jurisdiction = f"MSP {self.post_name} patrol zone"
        self.objective   = (
            "Maintain adequate highway coverage; meet district citation metrics; "
            "retain officers; stay within post budget; avoid officer injuries."
        )
        self.constraints = [
            "MELS CBA: cannot assign a specific trooper to a specific zone — seniority bid governs",
            "MELS CBA: minimum staffing per shift — cannot run below floor even if budget is tight",
            "MELS CBA: mandatory rest periods create dead zones around shift change",
            "Equipment scarcity: ~1 radar unit per 2.5 troopers — equipment follows seniority too",
            "Headcount: MSP has been short-staffed statewide since 2020 — posts are below authorized strength",
            "Jurisdiction seams: cannot direct troopers onto city streets or county roads",
            "Shift change dead zone: 30-60 min around shift transitions with minimal coverage",
        ]
        self.edges = [
            Edge("msp_leadership",  EdgeType.CONSTRAINED_BY, 3, "Receives district directives and metrics"),
            Edge("mels",            EdgeType.CONSTRAINED_BY, 3, "CBA constrains every staffing decision"),
            Edge("trooper",         EdgeType.COMMANDS,        3, "Daily tasking within CBA limits"),
            Edge("mpd",             EdgeType.COORDINATES,     1, "Informal coordination on incident response"),
            Edge("hc_sheriff",      EdgeType.COORDINATES,     1, "Jurisdiction hand-offs"),
        ]
        self.notes = (
            "The Post Commander's effective levers are narrow: "
            "(1) which road segments to emphasize in daily briefing, "
            "(2) equipment allocation (who gets the radar), "
            "(3) overtime approval for special enforcement details. "
            "Everything else — who patrols where, on which shift — is output of the seniority bid. "
            "Senior troopers have claimed the same desirable zones for years. "
            "Junior troopers cover the residual, often including the less-safe segments."
        )

    @property
    def effective_coverage_hours(self) -> float:
        """
        Estimate patrol coverage hours per day accounting for shift-change gaps.
        Dead zone: ~45 min per shift transition x 3 transitions = 2.25 hrs uncovered.
        """
        raw = 24.0
        shift_change_gap = 0.75 * self.shifts
        return raw - shift_change_gap

    def respond_to(self, pressure: dict) -> dict:
        ptype = pressure.get("type")

        if ptype == "budget_cut":
            pct = pressure.get("percent", 10)
            return {
                "response": "reduce_overtime_and_equipment_maintenance",
                "cascading_effects": [
                    f"Overtime budget cut ~{pct}% → special enforcement details cancelled",
                    "Deferred radar maintenance → fewer operational units per shift",
                    "Possible post consolidation if cut exceeds 20%",
                ],
                "note": (
                    "Cannot cut trooper headcount directly (MELS protects positions). "
                    "Budget pressure appears as equipment gaps and lost overtime, "
                    "which concentrates enforcement further on baseline safe-shoulder segments."
                )
            }

        if ptype == "staffing_shortage":
            return {
                "response": "triage_coverage_to_highest_incident_corridors",
                "note": (
                    "With fewer bodies, commander concentrates remaining troopers on "
                    "I-94/I-35W/I-494 core. Outer corridors (US-169, TH-55, TH-36) go thin. "
                    "Enforcement shadows on secondary routes expand significantly."
                )
            }

        if ptype == "political_directive":
            directive = pressure.get("directive", "increase citations")
            return {
                "response": "daily_briefing_emphasis",
                "note": (
                    f"Commander can emphasize '{directive}' in briefings and assign "
                    "equipment accordingly. Cannot force troopers to specific locations. "
                    "Effect: marginal shift in discretionary enforcement, not structural change."
                )
            }

        return {"response": "no_change", "note": f"Pressure '{ptype}' absorbed without behavioral change"}
