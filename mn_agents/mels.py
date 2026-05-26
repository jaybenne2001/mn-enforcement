"""
mn_agents/mels.py
MELS — Minnesota Law Enforcement Labor Services.
Represents MSP troopers in collective bargaining.

MELS is the single most structurally important institution in this model
for explaining citation geography. Its CBA provisions — seniority bidding,
minimum staffing, shift rules, approach protocols — constrain every
deployment decision from the Commissioner down to the individual trooper.

MELS is not a command institution. It does not deploy troopers.
It sets the rules within which all deployment decisions must operate.
Think of it as the constraint manifold for the entire MSP system.
"""

from dataclasses import dataclass, field
from typing import Optional
from .base import Institution, InstitutionType, Budget, Edge, EdgeType


@dataclass
class CBAProvision:
    article:     str
    title:       str
    description: str
    binds:       list[str]   # which institutions this constrains


# Key CBA provisions — inferred from standard MN public safety contracts
# (actual MELS CBA not fully public; these reflect PELRA norms + comparable CBAs)
MELS_KEY_PROVISIONS = [
    CBAProvision(
        article="Art. 12",
        title="Seniority Bidding",
        description=(
            "Troopers bid shift assignments and patrol zone preferences in reverse "
            "seniority order. Senior troopers select first. Management cannot override "
            "a valid bid. Result: senior troopers hold desirable zones indefinitely."
        ),
        binds=["post_commander", "msp_leadership", "msp_commissioner"],
    ),
    CBAProvision(
        article="Art. 14",
        title="Minimum Staffing",
        description=(
            "Each post must maintain a minimum number of troopers per shift. "
            "Cannot be reduced below floor even in budget shortfalls. "
            "This creates a fixed cost floor that limits budget flexibility."
        ),
        binds=["post_commander", "msp_leadership"],
    ),
    CBAProvision(
        article="Art. 16",
        title="Rest Between Shifts",
        description=(
            "Minimum 8 hours off between shifts. Creates a structural dead zone "
            "during shift transitions — typically 30-60 minutes of thin coverage "
            "3x per day. Consistent enforcement gaps at predictable times."
        ),
        binds=["post_commander"],
    ),
    CBAProvision(
        article="Art. 22",
        title="Officer Safety — Vehicle Approach",
        description=(
            "Officers must approach vehicles from the driver side unless a safety "
            "exception applies. On undivided roads without a shoulder, this exposes "
            "the officer to live traffic. Management cannot direct troopers to make "
            "unsafe approaches. Effectively prohibits stops on no-shoulder segments."
        ),
        binds=["trooper", "post_commander"],
    ),
    CBAProvision(
        article="Art. 8",
        title="Discipline Procedures",
        description=(
            "Progressive discipline with union representation at all stages. "
            "Management must document and follow process. Makes it difficult to "
            "discipline troopers for under-enforcement. Shifts management leverage "
            "toward metrics (activity reports) rather than direct supervision."
        ),
        binds=["post_commander", "msp_leadership", "msp_commissioner"],
    ),
    CBAProvision(
        article="Art. 19",
        title="Overtime and Special Details",
        description=(
            "Overtime must be offered in seniority order. Special enforcement "
            "details (NHTSA grant-funded speed campaigns) are overtime assignments. "
            "Senior troopers may decline. Means special details may not be staffed "
            "by the troopers best positioned geographically."
        ),
        binds=["post_commander", "msp_leadership"],
    ),
]


@dataclass
class MELS(Institution):

    represented_members: int = 2_400   # approximate MSP trooper count statewide
    contract_expiry:     str = "2025"  # renegotiated every 2 years under PELRA

    def __post_init__(self):
        self.id          = "mels"
        self.name        = "MELS — MN Law Enforcement Labor Services"
        self.type        = InstitutionType.UNION
        self.budget      = Budget(appropriated=0)  # funded by member dues, not appropriation
        self.headcount   = 12   # approximate MELS staff
        self.jurisdiction = "Statewide — MSP troopers, some other LE agencies"
        self.objective   = (
            "Maximize member wages, benefits, job security, and working conditions. "
            "Minimize management discretion over deployment, discipline, and safety. "
            "Maintain seniority as the primary organizing principle for assignment."
        )
        self.constraints = [
            "PELRA (MN Public Employment Labor Relations Act): governs bargaining rights and scope",
            "Must bargain in good faith — cannot unilaterally strike in most circumstances",
            "Arbitration is binding — bad arbitration outcomes set precedent",
            "Legislature can change PELRA — political vulnerability on labor law",
            "Public opinion: LE unions face heightened scrutiny post-2020",
        ]
        self.edges = [
            Edge("msp_commissioner",  EdgeType.CONSTRAINED_BY, 3, "Bargains CBA directly"),
            Edge("msp_leadership",    EdgeType.CONSTRAINED_BY, 3, "CBA binds operational decisions"),
            Edge("post_commander",    EdgeType.CONSTRAINED_BY, 3, "CBA binds shift/zone assignments"),
            Edge("trooper",           EdgeType.CONSTRAINED_BY, 3, "CBA governs every working condition"),
            Edge("afl_cio",           EdgeType.COORDINATES,    2, "Coalition labor politics"),
            Edge("hpsf",              EdgeType.INFLUENCES,     2, "Lobbies appropriations process"),
            Edge("sjps",              EdgeType.INFLUENCES,     2, "Lobbies on labor law and traffic statutes"),
        ]
        self.notes = (
            "MELS is the dominant constraint on MSP deployment geography. "
            "No other institution — not the Governor, not the Commissioner — can override "
            "the seniority bidding provisions in the CBA. This means the spatial distribution "
            "of enforcement is, in a real sense, a labor contract output, not a public safety output."
        )

    @property
    def key_provisions(self) -> list[CBAProvision]:
        return MELS_KEY_PROVISIONS

    def get_binding_constraints(self, for_institution: str) -> list[CBAProvision]:
        """Return CBA provisions that bind a specific institution."""
        return [p for p in MELS_KEY_PROVISIONS if for_institution in p.binds]

    def respond_to(self, pressure: dict) -> dict:
        ptype = pressure.get("type")

        if ptype == "budget_cut":
            return {
                "response": "grievance_and_arbitration",
                "note": (
                    "If budget cuts result in staffing below contract minimums, MELS files "
                    "grievance. Arbitration typically sides with union on clear CBA violations. "
                    "Management must find cuts elsewhere — equipment, training, overtime."
                )
            }

        if ptype == "deployment_override":
            return {
                "response": "unfair_labor_practice_charge",
                "note": (
                    "Any attempt to assign troopers to specific zones outside the bid process "
                    "triggers ULP charge with BMS (Bureau of Mediation Services). "
                    "Strong precedent in MN for union on seniority bid rights."
                )
            }

        if ptype == "political_scrutiny":
            return {
                "response": "public_relations_and_legislative_engagement",
                "note": (
                    "MELS engages AFL-CIO coalition, makes member safety arguments, "
                    "lobbies friendly legislators. Digs in on contract provisions. "
                    "Post-2020 environment has made this harder but not structurally changed outcomes."
                )
            }

        return {"response": "monitor_and_hold", "note": f"No immediate response to '{ptype}'"}
