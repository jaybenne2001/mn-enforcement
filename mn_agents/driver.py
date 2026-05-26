"""
mn_agents/driver.py
The Driver — the adversary at the bottom of the hierarchy.

The driver is the only actor in this system who does not say yes to anything.
Every other institution has a principal it reports to and constraints it
operates within. The driver answers to no one. They optimize purely for
travel time and risk avoidance.

Critically: the driver is the fastest-adapting actor in the system.
Institutions update their behavior on the scale of budget cycles (1-2 years)
or contract cycles (2 years). The driver updates on the scale of a single
drive — they share knowledge via Waze, adjust speeds in real time, and
develop mental models of enforcement geography through repeated experience.

This is why enforcement patterns persist but specific traps become known.
"""

from dataclasses import dataclass
from .base import Institution, InstitutionType, Budget, Edge, EdgeType


@dataclass
class KnowledgeModel:
    """What the driver knows (or believes) about enforcement geography."""
    known_hotspots:     list[str] = None    # locations learned from experience/Waze
    known_dead_zones:   list[str] = None    # segments perceived as unpatrolled
    shift_timing_known: bool      = False   # does driver know shift change windows
    radar_type_known:   bool      = False   # does driver know MSP uses LIDAR vs radar

    def __post_init__(self):
        self.known_hotspots   = self.known_hotspots   or []
        self.known_dead_zones = self.known_dead_zones or []


@dataclass
class Driver(Institution):

    commute_route:     str   = "I-94 westbound"
    avg_speed_over:    int   = 8     # mph over posted limit on open highway
    waze_user:         bool  = True  # uses real-time enforcement alerts
    knowledge:         KnowledgeModel = None

    def __post_init__(self):
        self.id          = "driver"
        self.name        = "Driver"
        self.type        = InstitutionType.DRIVER
        self.budget      = Budget(appropriated=0)
        self.headcount   = 1
        self.jurisdiction = "Wherever they're going"
        self.objective   = (
            "Minimize travel time subject to acceptable citation risk. "
            "Not: obey speed limits. Citation risk is the actual constraint, "
            "not the posted limit."
        )
        self.constraints = [
            "Physical: vehicle capability and road conditions",
            "Social: Waze and crowd-sourced enforcement knowledge (reduces information asymmetry)",
            "Economic: citation cost + insurance impact + potential license suspension",
            "Temporal: time pressure from commute schedule, trip purpose",
        ]
        self.edges = [
            Edge("trooper",       EdgeType.ADVERSARIAL, 3, "Primary enforcement contact"),
            Edge("dist_court",    EdgeType.CONSTRAINED_BY, 2, "Contest or pay citations"),
        ]
        self.notes = (
            "The driver's information advantage grows over time. "
            "Waze provides real-time enforcement location data. "
            "Repeated driving on the same route builds a mental model of "
            "where stops happen and don't happen. "
            "Enforcement shadows (no-shoulder segments, shift-change windows) "
            "become known through community knowledge. "
            "This creates a game-theoretic equilibrium where enforcement patterns "
            "are both persistent (institution-driven) and partly anticipated (driver-adapted)."
        )
        if self.knowledge is None:
            self.knowledge = KnowledgeModel()

    def assess_risk(self, segment: dict) -> dict:
        """
        Driver's perceived risk assessment for a road segment.
        Input: segment dict with keys: name, has_shoulder, jurisdiction, known_hotspot, time_of_day
        """
        risk_score = 0
        factors = []

        if segment.get("known_hotspot"):
            risk_score += 3
            factors.append("Known enforcement location — slow to posted limit")

        if segment.get("has_shoulder"):
            risk_score += 1
            factors.append("Pullout available — stop physically possible")

        if segment.get("jurisdiction") == "MSP":
            risk_score += 1
            factors.append("MSP corridor — active patrol jurisdiction")

        tod = segment.get("time_of_day", "")
        if tod in ["morning_rush", "afternoon_rush"]:
            risk_score -= 1
            factors.append("Rush hour — traffic density reduces individual targeting")
        elif tod == "shift_change":
            risk_score -= 2
            factors.append("Shift change window — historically low enforcement activity")
        elif tod in ["10am", "2pm"]:
            risk_score += 1
            factors.append("Mid-shift — peak enforcement period")

        if self.waze_user and segment.get("waze_alert"):
            risk_score += 2
            factors.append("Active Waze alert — confirmed enforcement present")

        return {
            "segment": segment.get("name", "unknown"),
            "risk_score": risk_score,
            "max_comfortable_speed_over": max(0, 15 - risk_score * 2),
            "factors": factors,
        }

    def respond_to(self, pressure: dict) -> dict:
        ptype = pressure.get("type")

        if ptype == "new_enforcement_location":
            return {
                "response": "adapt_within_1-3_weeks",
                "note": (
                    "Waze community updates typically within days of a new enforcement location. "
                    "Driver adapts speed on that segment. Trooper's citation rate at that "
                    "location drops. Enforcement 'moves' or becomes less productive. "
                    "This is the fastest feedback loop in the system."
                )
            }

        if ptype == "fine_increase":
            amount = pressure.get("amount_increase", 50)
            return {
                "response": "marginal_behavior_change",
                "note": (
                    f"${amount} fine increase shifts risk calculus slightly. "
                    "Effect is largest for low-income drivers (budget constraint binding). "
                    "For drivers where the fine is noise relative to income, "
                    "behavioral change is minimal. Speed limit compliance is not the output."
                )
            }

        if ptype == "waze_disabled":
            return {
                "response": "revert_to_experience_based_model",
                "note": (
                    "Without Waze, drivers rely on personal route knowledge. "
                    "Known hotspots from memory still shape behavior. "
                    "New enforcement locations take longer to enter the community model. "
                    "Short-term enforcement effectiveness increases; degrades within weeks."
                )
            }

        return {"response": "no_change", "note": f"Pressure '{ptype}' not salient to driver"}
