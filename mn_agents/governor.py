"""
mn_agents/governor.py
Minnesota Governor — the apex political actor in this system.

The Governor's relationship to traffic enforcement is almost entirely indirect.
They appoint the MSP Commissioner, influence the DPS budget request, and respond
to media pressure. They have no operational levers inside MSP. The MELS contract
runs beneath them — a Governor cannot unilaterally change union contract terms.

Key dynamic: the Governor needs MELS/AFL-CIO endorsements in election cycles.
This creates a structural disincentive to push hard on any reform that MELS opposes.
"""

from dataclasses import dataclass
from .base import Institution, InstitutionType, Budget, Edge, EdgeType


@dataclass
class Governor(Institution):

    incumbent:         str  = "Tim Walz"
    election_year:     int  = 2026
    labor_endorsed:    bool = True   # AFL-CIO endorsement in last cycle

    def __post_init__(self):
        self.id          = "governor"
        self.name        = "Governor of Minnesota"
        self.type        = InstitutionType.STATE_EXEC
        self.budget      = Budget(appropriated=0)  # Governor's office is overhead
        self.headcount   = 60   # Governor's office staff
        self.jurisdiction = "Statewide executive authority"
        self.objective   = (
            "Maintain public safety credibility; manage political coalition "
            "(labor, progressive, suburban); avoid embarrassing incidents; "
            "position for re-election or successor endorsement."
        )
        self.constraints = [
            "Legislature: budget requires legislative appropriation — cannot unilaterally fund MSP",
            "MELS/AFL-CIO: union endorsement valuable; aggressive anti-union moves costly",
            "PELRA: cannot change public employee union rights by executive action",
            "Media cycle: MSP incidents become Governor's incidents",
            "Federal compliance: state must maintain federal highway safety standards or lose FHWA funds",
            "DFL coalition: progressive wing skeptical of expanded enforcement; suburban wing wants it",
        ]
        self.edges = [
            Edge("dps",           EdgeType.COMMANDS,        3, "Appoints DPS Commissioner"),
            Edge("mmb",           EdgeType.COMMANDS,        2, "Budget priorities filter through MMB"),
            Edge("msp_commissioner", EdgeType.COMMANDS,     3, "Appoints MSP Commissioner"),
            Edge("hpsf",          EdgeType.INFLUENCES,      2, "Legislative budget negotiation"),
            Edge("sjps",          EdgeType.INFLUENCES,      2, "Legislative policy negotiation"),
            Edge("afl_cio",       EdgeType.CONSTRAINED_BY,  2, "Labor endorsement dependency"),
            Edge("star_trib",     EdgeType.CONSTRAINED_BY,  1, "Media pressure on public safety"),
        ]
        self.notes = (
            "The Governor's practical levers on traffic enforcement are: "
            "(1) Commissioner appointment — strongest lever, sets tone for entire MSP. "
            "(2) Budget request — DPS prepares it but Governor signals priorities. "
            "(3) Legislative advocacy — can push for MSP funding increases. "
            "What the Governor cannot do: tell a trooper where to stand, override a CBA, "
            "or create coverage on a road without a shoulder."
        )

    def respond_to(self, pressure: dict) -> dict:
        ptype = pressure.get("type")

        if ptype == "fatal_accident_on_highway":
            return {
                "response": "public_statement_and_commissioner_call",
                "note": (
                    "Governor issues public safety statement, calls MSP Commissioner "
                    "for briefing. May announce 'increased enforcement' initiative. "
                    "Practical effect: commissioner issues district directive; "
                    "post commanders hold briefings; troopers' behavior shifts marginally "
                    "for 2-3 weeks, then returns to baseline."
                )
            }

        if ptype == "budget_pressure":
            direction = pressure.get("direction", "cut")
            if direction == "cut":
                return {
                    "response": "protect_public_safety_appropriation",
                    "note": (
                        "Governor resists MSP cuts publicly — too politically costly. "
                        "More likely to find cuts in other DPS programs. "
                        "MSP headcount is the last thing a Governor cuts before an election."
                    )
                }
            else:
                return {
                    "response": "propose_trooper_hiring_initiative",
                    "note": (
                        "Popular bipartisan move. Legislature usually supportive. "
                        "New hires take 18 months to deploy (academy pipeline). "
                        "Effect on enforcement geography: fills residual zones, "
                        "does not displace senior troopers from established positions."
                    )
                }

        if ptype == "racial_disparity_report":
            return {
                "response": "commission_review_and_defer",
                "note": (
                    "Governor orders DPS review of citation data. Commissioner "
                    "produces report. Outcome typically: implicit bias training, "
                    "updated stop data collection. No structural change to seniority "
                    "bidding or deployment geography — those are CBA issues the "
                    "Governor cannot touch without union consent."
                )
            }

        return {"response": "no_direct_action", "note": f"Pressure '{ptype}' handled at agency level"}
