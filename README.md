# mn-enforcement

A systems-level analysis of Minnesota traffic enforcement — modeled as a network of institutional agents, visualized as a budget cascade, and grounded in actual citation geography.

## What's here

### `mn_enforcement_map_gmaps.html`
Interactive Twin Cities enforcement map built from MSP citation data. Shows where troopers actually write tickets, marks hotspot types, and predicts which locations are likely active based on time of day and shift patterns. Open in Chrome or Safari — no install needed.

### `mn_power_structure.html`
Network diagram of the 27 institutional actors and 35 directed relationships that govern traffic enforcement in Minnesota. 9-tier hierarchy from federal funding down to the driver. Click nodes to explore. Built to run on a wide display.

### `mn_agents/`
Python module modeling each institution as an agent with an objective function, constraint set, and behavioral responses to external pressure.

```
mn_agents/
├── base.py            # Institution base class — Budget, Edge, EdgeType
├── trooper.py         # Street-level actor. StopConditions, evaluate_stop()
├── post_commander.py  # Field command. Coverage hours, budget cut cascades
├── msp_leadership.py  # Statewide ops. Vacancy rate, NHTSA grant compliance
├── governor.py        # Political layer. Labor endorsement dependency
├── mels.py            # Union constraint. 6 CBA provisions as structured objects
├── driver.py          # The adversary. Risk assessment, Waze adaptation
└── simulation.py      # Scenario runner. Propagate pressure through the chain
```

**Run the demo:**
```bash
cd mn-enforcement
python -m mn_agents.simulation
```

Outputs two scenarios:
- Legislature cuts MSP budget 15% → cascades through MELS, equipment, coverage, driver
- Stop evaluation with/without shoulder → enforcement shadow logic

## Key insight

The spatial distribution of MSP enforcement is not a public safety output. It is the joint product of:
- Seniority bidding under the MELS collective bargaining agreement (troopers pick zones, management can't override)
- Road geometry (stops require a paved shoulder — no shoulder = enforcement shadow)
- Federal grant performance targets (NHTSA shapes citation priorities for ~$18M/yr)
- Shift change dead zones (3× daily, 45 min each)

The Governor, the Legislature, and MSP leadership cannot place a specific trooper at a specific location. The union contract runs beneath all of them.

## Budget context

Minnesota's $66B biennial budget reaches MSP at approximately $400M — roughly 0.6% of the total. Fine revenue from citations goes to county general funds, not back to MSP. There is no financial feedback loop between enforcement activity and the agency budget.

## Legal layer

Driver chess moves grounded in statute:
- **MN Stat. §169.14, subd. 10** — foundation requirements for speed measurement evidence; calibration records available to defendant on demand
- **MN Stat. §169.91** — citation signature is promise to appear, not admission of guilt
- **MRE 801(d)(2)** — anything you say at the window is an admission by party-opponent, fully admissible

## Data sources

- MSP citation data: [MN Department of Public Safety open data](https://dps.mn.gov)
- Road geometry: [MnDOT open data](https://www.dot.state.mn.us/maps/gdma/)
- Budget: [MN Management & Budget](https://mn.gov/mmb/budget/)
- MELS CBA: filed with MN Bureau of Mediation Services

## Status

Active. Agents for Legislature, MPD, Hennepin Sheriff, and District Court are next. Budget/contract empirical model in progress.
