"""
mn_agents/simulation.py
Scenario runner — propagate a pressure through the institution chain.

Usage:
    from mn_agents.simulation import EnforcementSystem, Scenario

    system = EnforcementSystem()
    result = system.run(Scenario(type="budget_cut", percent=15))
    print(result.summary())
"""

from dataclasses import dataclass, field
from typing import Any

from .base        import Institution
from .governor    import Governor
from .msp_leadership import MSPLeadership
from .post_commander import PostCommander
from .trooper     import Trooper, StopConditions
from .mels        import MELS
from .driver      import Driver


@dataclass
class Scenario:
    """
    Common scenario types:
      budget_cut              percent=10-30
      staffing_shortage       (uses current vacancy)
      quota_pressure
      media_scrutiny
      legislature_mandate     directive="..."
      fatal_accident_on_highway
      fine_increase           amount_increase=50
      new_enforcement_location
    """
    type:   str
    label:  str  = ""
    params: dict = field(default_factory=dict)


@dataclass
class ScenarioResult:
    scenario:   Scenario
    responses:  dict[str, dict]   # institution_id → response dict
    cascade:    list[str]         # narrative of propagation

    def summary(self) -> str:
        lines = [
            f"SCENARIO: {self.scenario.label or self.scenario.type}",
            "=" * 60,
        ]
        for inst_id, resp in self.responses.items():
            lines.append(f"\n[{inst_id}]")
            lines.append(f"  Response: {resp.get('response', '—')}")
            note = resp.get('note') or resp.get('note', '')
            if note:
                lines.append(f"  Note:     {note}")
            if 'impacts' in resp:
                lines.append("  Impacts:")
                for imp in resp['impacts']:
                    lines.append(f"    • {imp}")
            if 'cascading_effects' in resp:
                lines.append("  Cascading effects:")
                for eff in resp['cascading_effects']:
                    lines.append(f"    • {eff}")
        if self.cascade:
            lines += ["", "PROPAGATION CHAIN:", "─" * 40]
            for step in self.cascade:
                lines.append(f"  → {step}")
        return "\n".join(lines)


class EnforcementSystem:
    """
    Instantiates all enforcement-spine institutions and routes
    a scenario through the relevant chain.
    """

    def __init__(self):
        self.governor      = Governor()
        self.msp_lead      = MSPLeadership()
        self.post_cmd      = PostCommander()
        self.trooper       = Trooper()
        self.mels          = MELS()
        self.driver        = Driver()

        # Ordered enforcement spine — pressure propagates top-down
        self.spine: list[Institution] = [
            self.governor,
            self.msp_lead,
            self.post_cmd,
            self.trooper,
        ]

        # Cross-cutting constraint — applied at every level
        self.constraint_layer = self.mels

    def run(self, scenario: Scenario) -> ScenarioResult:
        pressure = {"type": scenario.type, **scenario.params}

        responses = {}
        cascade   = []

        # Propagate through spine
        for inst in self.spine:
            try:
                resp = inst.respond_to(pressure)
                responses[inst.id] = resp
                cascade.append(
                    f"{inst.name}: {resp.get('response', '—')}"
                )
            except NotImplementedError:
                responses[inst.id] = {"response": "not_modeled"}

        # Apply union constraint layer
        try:
            mels_resp = self.mels.respond_to(pressure)
            responses["mels"] = mels_resp
            if mels_resp.get("response") not in ("no_change", "monitor_and_hold"):
                cascade.append(
                    f"MELS (constraint): {mels_resp.get('response', '—')}"
                )
        except NotImplementedError:
            pass

        # Driver adaptation (bottom of system)
        try:
            driver_resp = self.driver.respond_to(pressure)
            responses["driver"] = driver_resp
            cascade.append(
                f"Driver: {driver_resp.get('response', '—')}"
            )
        except NotImplementedError:
            pass

        return ScenarioResult(scenario=scenario, responses=responses, cascade=cascade)

    def run_stop_evaluation(
        self,
        shoulder: bool,
        approach_safe: bool,
        jurisdiction: bool,
        equipment: bool,
        shift_active: bool,
        mph_over: int,
    ) -> dict:
        """Run a single stop decision through the trooper agent."""
        conditions = StopConditions(
            safe_shoulder   = shoulder,
            approach_safe   = approach_safe,
            jurisdiction    = jurisdiction,
            equipment_ready = equipment,
            shift_active    = shift_active,
        )
        return self.trooper.evaluate_stop(conditions, mph_over)


# ── quick demo ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    system = EnforcementSystem()

    print("\n" + "─"*60)
    print("SCENARIO 1: Legislature cuts MSP budget 15%")
    print("─"*60)
    result = system.run(Scenario(type="budget_cut", label="15% budget cut", params={"percent": 15}))
    print(result.summary())

    print("\n" + "─"*60)
    print("SCENARIO 2: Stop evaluation — no shoulder, 22 mph over")
    print("─"*60)
    decision = system.run_stop_evaluation(
        shoulder=False, approach_safe=False, jurisdiction=True,
        equipment=True, shift_active=True, mph_over=22
    )
    print(f"Decision: {decision['decision']}")
    print(f"Reason:   {decision['reason']}")
    print(f"Enforcement shadow created: {decision.get('enforcement_shadow', False)}")

    print("\n" + "─"*60)
    print("SCENARIO 3: Safe shoulder, 22 mph over, mid-shift")
    print("─"*60)
    decision2 = system.run_stop_evaluation(
        shoulder=True, approach_safe=True, jurisdiction=True,
        equipment=True, shift_active=True, mph_over=22
    )
    print(f"Decision: {decision2['decision']}")
    print(f"Reason:   {decision2['reason']}")
