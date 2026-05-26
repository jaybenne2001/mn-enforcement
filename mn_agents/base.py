"""
mn_agents/base.py
Base class for all Minnesota enforcement institution agents.
Each institution has an objective function, a constraint set, and behaviors.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class InstitutionType(str, Enum):
    FEDERAL      = "federal"
    STATE_EXEC   = "state_executive"
    STATE_LEGIS  = "state_legislative"
    MSP          = "msp"
    UNION        = "union"
    LOCAL        = "local_agency"
    JUDICIAL     = "judicial"
    CIVIC        = "civic"
    DRIVER       = "driver"


class EdgeType(str, Enum):
    COMMANDS        = "commands"
    CONSTRAINED_BY  = "constrained_by"
    RESOURCES_FROM  = "resources_from"
    OVERSEES        = "oversees"
    COORDINATES     = "coordinates_with"
    INFLUENCES      = "influences"
    ADVERSARIAL     = "adversarial"


@dataclass
class Budget:
    appropriated:    float        # annual state/local appropriation, USD
    federal_grants:  float = 0.0  # NHTSA, FHWA, etc.
    other:           float = 0.0

    @property
    def total(self) -> float:
        return self.appropriated + self.federal_grants + self.other

    def __str__(self) -> str:
        return f"${self.total/1_000_000:.1f}M (appropriated: ${self.appropriated/1_000_000:.1f}M)"


@dataclass
class Edge:
    target_id:  str
    edge_type:  EdgeType
    weight:     int = 1   # 1=weak, 2=moderate, 3=strong
    note:       str = ""


@dataclass
class Institution:
    """
    Base class. Each institution is modeled as an agent with:
      - An objective function (what it maximizes)
      - Constraints (what limits its behavior)
      - Edges (relationships to other institutions)
      - Behaviors (how it responds to scenarios)
    """
    id:          str            = ""
    name:        str            = ""
    type:        InstitutionType = InstitutionType.MSP
    budget:      Budget         = field(default_factory=lambda: Budget(0))
    headcount:   int            = 0
    jurisdiction: str           = ""
    objective:   str            = ""
    constraints: list[str]      = field(default_factory=list)
    edges:       list[Edge]     = field(default_factory=list)
    notes:       str            = ""

    # ── core interface ────────────────────────────────────────────────────

    def get_objective(self) -> dict:
        """
        Return a structured representation of what this institution maximizes.
        Override in subclasses for quantitative modeling.
        """
        return {"maximize": self.objective, "subject_to": self.constraints}

    def get_active_constraints(self, scenario: Optional[dict] = None) -> list[str]:
        """
        Return constraints that are binding under a given scenario.
        Default: return all. Override to make scenario-sensitive.
        """
        return self.constraints

    def respond_to(self, pressure: dict) -> dict:
        """
        Given an external pressure (budget cut, media event, political directive),
        return this institution's likely response. Override in subclasses.
        """
        raise NotImplementedError(f"{self.name}.respond_to() not implemented")

    def describe(self) -> str:
        lines = [
            f"{'='*60}",
            f"{self.name}  [{self.type.value}]",
            f"{'='*60}",
            f"Budget:     {self.budget}",
            f"Headcount:  {self.headcount:,}",
            f"Jurisdiction: {self.jurisdiction}",
            f"",
            f"Objective:  {self.objective}",
            f"",
            f"Constraints:",
        ]
        for c in self.constraints:
            lines.append(f"  • {c}")
        if self.edges:
            lines.append("")
            lines.append("Relationships:")
            for e in self.edges:
                lines.append(f"  {e.edge_type.value:20s} → {e.target_id}  (w={e.weight})")
        if self.notes:
            lines += ["", "Notes:", self.notes]
        return "\n".join(lines)
