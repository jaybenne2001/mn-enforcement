"""
mn_agents/msp_leadership.py
MSP Leadership (Command Staff below Commissioner).

Translates Commissioner/DPS directives into district-level operations.
Manages statewide deployment strategy, grant compliance, and inter-agency
coordination. Constrained above by politics and budget; constrained below
by the MELS contract. Squeezed from both directions.
"""

from dataclasses import dataclass
from .base import Institution, InstitutionType, Budget, Edge, EdgeType


@dataclass
class MSPLeadership(Institution):

    districts:         int = 7    # MSP patrol districts statewide
    authorized_strength: int = 2_400
    actual_strength:   int = 2_100   # MSP has been below authorized since ~2020

    def __post_init__(self):
        self.id          = "msp_leadership"
        self.name        = "MSP Leadership (Command Staff)"
        self.type        = InstitutionType.MSP
        self.budget      = Budget(
            appropriated   = 180_000_000,  # MSP patrol ops ~$180M (rough)
            federal_grants =  18_000_000,  # NHTSA grants ~$18M
        )
        self.headcount   = self.actual_strength
        self.jurisdiction = "All MN state highways and interstates, statewide"
        self.objective   = (
            "Meet NHTSA grant performance targets (DUI, speed, seatbelt citations); "
            "maintain adequate statewide coverage; stay within appropriation; "
            "manage legislative relationships; minimize officer injuries."
        )
        self.constraints = [
            "MELS CBA: cannot direct individual trooper placement — seniority bid governs",
            "Legislative appropriation: hard budget ceiling with no carryforward",
            "NHTSA grant compliance: must hit performance targets or lose federal funding",
            "Staffing shortage: ~300 below authorized strength as of 2024 — 12.5% gap",
            "Cannot compel troopers to work overtime beyond CBA limits",
            "Inter-agency deconfliction: must coordinate with MPD/Sheriff on jurisdiction seams",
        ]
        self.edges = [
            Edge("msp_commissioner",  EdgeType.CONSTRAINED_BY, 3, "Receives mission and budget"),
            Edge("mels",              EdgeType.CONSTRAINED_BY, 3, "CBA limits all deployment decisions"),
            Edge("post_commander",    EdgeType.COMMANDS,        3, "Directs district operations"),
            Edge("mpd",               EdgeType.COORDINATES,     2, "Metro incident coordination"),
            Edge("hc_sheriff",        EdgeType.COORDINATES,     2, "Jurisdiction overlap management"),
            Edge("nhtsa",             EdgeType.RESOURCES_FROM,  2, "Grant funding and compliance"),
        ]
        self.notes = (
            "The staffing shortage is the critical operational variable right now. "
            "MSP is ~300 troopers below authorized strength statewide. "
            "In the metro district, this means post commanders are running shifts "
            "at or near minimum staffing levels. Every trooper who calls in sick "
            "creates a coverage gap that cannot be filled without overtime — "
            "which must be offered to senior troopers first, compounding the "
            "seniority sorting problem."
        )

    @property
    def vacancy_rate(self) -> float:
        return 1 - (self.actual_strength / self.authorized_strength)

    def respond_to(self, pressure: dict) -> dict:
        ptype = pressure.get("type")

        if ptype == "budget_cut":
            pct = pressure.get("percent", 10)
            impacts = []
            if pct >= 5:
                impacts.append("Freeze equipment purchases — radar/LIDAR replacement deferred")
            if pct >= 10:
                impacts.append("Cancel NHTSA-funded special enforcement campaigns")
                impacts.append("Hiring freeze extends vacancy rate further")
            if pct >= 20:
                impacts.append("Post consolidation — some rural posts merge")
                impacts.append("Metro coverage drops to statutory minimum staffing")
            return {
                "response": "triage_by_priority",
                "impacts": impacts,
                "note": (
                    f"A {pct}% cut cannot touch trooper salaries (MELS protected). "
                    "Everything else is on the table. Grant compliance at risk if cuts "
                    "eliminate the programs tied to NHTSA performance targets."
                )
            }

        if ptype == "legislature_mandate":
            directive = pressure.get("directive", "")
            return {
                "response": "issue_district_directive",
                "note": (
                    f"Leadership can issue directive to districts: '{directive}'. "
                    "Practical effect depends on whether it requires specific trooper placement "
                    "(blocked by MELS) or just emphasis in daily briefing (allowed)."
                )
            }

        if ptype == "staffing_improvement":
            new_hires = pressure.get("count", 50)
            return {
                "response": "junior_troopers_fill_residual_zones",
                "note": (
                    f"{new_hires} new hires enter at bottom of seniority. "
                    "They do not displace senior troopers from bid zones. "
                    "They fill the residual coverage gaps — often the less desirable "
                    "and less safe segments that senior troopers passed over."
                )
            }

        return {"response": "absorb_and_continue", "note": f"Pressure '{ptype}' has no immediate structural effect"}
