"""
mn_agents — Minnesota enforcement institution agent models.

Enforcement spine (command hierarchy):
    Governor → MSPLeadership → PostCommander → Trooper

Constraint layer (cross-cutting):
    MELS (union CBA)

Adversarial actor:
    Driver

Usage:
    from mn_agents.simulation import EnforcementSystem, Scenario
    system = EnforcementSystem()
    result = system.run(Scenario(type="budget_cut", percent=15))
    print(result.summary())
"""

from .base            import Institution, InstitutionType, Budget, Edge, EdgeType
from .trooper         import Trooper, StopConditions
from .post_commander  import PostCommander
from .msp_leadership  import MSPLeadership
from .governor        import Governor
from .mels            import MELS, CBAProvision
from .driver          import Driver, KnowledgeModel
from .simulation      import EnforcementSystem, Scenario, ScenarioResult

__all__ = [
    "Institution", "InstitutionType", "Budget", "Edge", "EdgeType",
    "Trooper", "StopConditions",
    "PostCommander",
    "MSPLeadership",
    "Governor",
    "MELS", "CBAProvision",
    "Driver", "KnowledgeModel",
    "EnforcementSystem", "Scenario", "ScenarioResult",
]
