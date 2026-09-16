# AMIE — Agricultural Market Infeasibility Engine
## Product Requirements Document (PRD)
### Final Revised Build Specification

**Document status:** Build-ready MVP specification  
**Primary goal:** A fully software-based, free-to-build agricultural market feasibility and intervention simulator that can be implemented by an IDE coding agent.

---

# 1. Product Definition

## 1.1 Name
**AMIE — Agricultural Market Infeasibility Engine**

## 1.2 One-line pitch
**AMIE finds agricultural futures that cannot physically happen—and calculates the cheapest intervention that makes them feasible.**

## 1.3 Core problem

Agricultural markets can look healthy in aggregate while future commitments create an impossible physical state.

Examples:

- harvest arrivals exceed buyer absorption;
- processing capacity is exceeded during a synchronized harvest;
- storage fills before all expected produce can be moved;
- transport capacity becomes the bottleneck;
- buyer demand exists but cannot absorb the right commodity/quality/time window;
- several individually reasonable commitments become collectively infeasible.

AMIE does not primarily predict prices or act as a marketplace. Its core job is:

> Given the best currently available estimate of future agricultural supply, demand, infrastructure capacity, and commitments, determine whether a physically feasible path exists from production to an end destination.

If not, AMIE identifies the constraint causing infeasibility and computes feasible interventions.

---

# 2. Product Principles

1. **Forecasting is an input, not the product.**
2. **Optimization is downstream of feasibility detection.**
3. **The system must distinguish observed data, inferred data, and synthetic demo data.**
4. **No fabricated real-world claims.**
5. **No paid APIs or proprietary datasets are required for MVP.**
6. **Every model output must expose assumptions.**
7. **Every intervention must be traceable to constraints and quantities.**
8. **LLM is optional and only used for explanation; deterministic calculations remain the source of truth.**
9. **The MVP must work completely offline after data/model assets are downloaded.**
10. **The demo must be reproducible from a fixed scenario seed.**

---

# 3. Target Users

## Primary
- Agricultural planners
- Procurement managers
- Farmer-producer organizations
- Cooperatives
- Processors
- Warehouses/storage operators
- Government/agricultural supply-chain planners

## Secondary
- Researchers
- Agritech analysts
- Disaster/agricultural resilience planners

The hackathon MVP is designed primarily for evaluator demonstration, not immediate production deployment.

---

# 4. Core User Story

A planner selects:

- region;
- commodity;
- forecast horizon;
- current market state;
- expected farmer harvest commitments;
- buyer demand;
- processing capacity;
- storage capacity;
- transport capacity.

AMIE then:

1. reconstructs the future network;
2. predicts/estimates future flows;
3. checks physical feasibility;
4. identifies the first infeasible time/node;
5. explains the bottleneck;
6. identifies the critical commitments/flows;
7. generates intervention options;
8. simulates each intervention;
9. compares outcomes;
10. displays the cheapest feasible recovery.

---

# 5. Scope

## 5.1 MVP IN SCOPE

### Data
- historical agricultural market prices;
- market arrivals;
- crop production/yield;
- weather;
- geographic distances;
- market/warehouse/processor/buyer locations;
- synthetic farmer commitments;
- synthetic buyer demand;
- synthetic processing/storage/transport capacities.

### Computation
- supply forecasting;
- demand estimation;
- arrival-window generation;
- capacity modelling;
- network construction;
- feasibility checking;
- bottleneck detection;
- critical-flow analysis;
- intervention optimization;
- scenario simulation;
- counterfactual comparison.

### UI
- scenario setup;
- map/network;
- forecast timeline;
- capacity utilization;
- infeasibility alert;
- bottleneck explanation;
- intervention comparison;
- before/after metrics.

## 5.2 OUT OF SCOPE FOR MVP

- live trading;
- actual procurement;
- payments;
- autonomous communication with farmers;
- direct tractor control;
- proprietary satellite-processing pipelines;
- hardware sensors;
- guaranteed real-world price prediction;
- production deployment;
- autonomous government decision-making.

---

# 6. System Architecture

```text
                    PUBLIC DATA
                       |
        +--------------+--------------+
        |              |              |
     Market         Weather       Production
      Data            Data           Data
        |              |              |
        +--------------+--------------+
                       |
                DATA NORMALIZER
                       |
                       v
              AGRICULTURAL STATE
                 ESTIMATOR
                       |
          +------------+------------+
          |            |            |
       SUPPLY       DEMAND       CAPACITY
       STATE        STATE         STATE
          |            |            |
          +------------+------------+
                       |
                 FORECAST ENGINE
                       |
                       v
              FUTURE COMMITMENTS
                       |
                       v
              NETWORK BUILDER
                       |
                       v
             FEASIBILITY ENGINE
                       |
              +--------+--------+
              |                 |
          FEASIBLE          INFEASIBLE
              |                 |
              |            BOTTLENECK ENGINE
              |                 |
              |            CRITICAL SET
              |                 |
              |          INTERVENTION ENGINE
              |                 |
              +--------+--------+
                       |
                 COUNTERFACTUAL
                   SIMULATOR
                       |
                       v
                 AMIE RESULT
                       |
             +---------+---------+
             |                   |
         DASHBOARD          EXPLANATION
```

---

# 7. Data Strategy — ZERO-COST MVP

## 7.1 Required rule

Every external dataset must be:

- publicly accessible;
- downloadable without payment;
- legally usable for the prototype;
- reproducible by teammates;
- stored locally after acquisition.

Do not make the application dependent on an API that may require a key.

## 7.2 Recommended sources

### India / agriculture
Use government/open-data sources where practical:

- India Open Government Data Platform (data.gov.in)
- Directorate of Marketing & Inspection / AGMARKNET datasets
- e-NAM public market information
- Kerala Department of Economics & Statistics market datasets
- Kerala agricultural statistics
- Directorate of Economics & Statistics agriculture datasets

### Weather
- Open-Meteo historical weather API/data
- NASA POWER
- Copernicus climate/environment datasets where required

### Geography
- OpenStreetMap / Geofabrik extracts
- Natural Earth for administrative boundaries

### Research validation
- published agricultural datasets from openly accessible repositories;
- Kaggle only when licensing permits and the exact dataset license is recorded.

## 7.3 Data acquisition policy

Create:

```text
data/
  raw/
  processed/
  external/
  synthetic/
  metadata/
```

Every downloaded dataset gets:

```text
dataset_name
source_url
access_date
license
geographic_scope
temporal_scope
columns
units
preprocessing
```

Create:

```text
data/metadata/DATA_SOURCES.md
```

No undocumented dataset enters the project.

---

# 8. MVP Dataset Design

## 8.1 Market observation

```text
date
state
district
market_id
commodity
arrival_kg
wholesale_price
retail_price
unit
```

## 8.2 Production

```text
season
state
district
commodity
area_hectare
production_tonnes
yield_t_per_ha
```

## 8.3 Weather

```text
date
latitude
longitude
temperature
precipitation
et0
```

## 8.4 Farmer commitment

Synthetic MVP entity:

```text
farmer_id
location
commodity
expected_harvest_date
expected_quantity_kg
quality_grade
minimum_price
available_from
available_until
```

## 8.5 Buyer

```text
buyer_id
location
commodity
required_quantity_kg
minimum_quality
demand_date
maximum_procurement_kg
```

## 8.6 Processing facility

```text
processor_id
location
commodity
daily_capacity_kg
current_load_kg
quality_requirement
operating_days
```

## 8.7 Storage

```text
storage_id
location
commodity
capacity_kg
current_inventory_kg
daily_inflow_limit_kg
daily_outflow_limit_kg
```

## 8.8 Transport edge

```text
source_id
destination_id
distance_km
daily_capacity_kg
transport_cost_per_kg_km
travel_time_hours
```

---

# 9. Synthetic Data Policy

Synthetic data is acceptable and expected for micro-level commitments where public datasets do not expose individual actors.

But:

**Never present synthetic values as real farmers, real buyers, or real facilities.**

UI label:

> DEMONSTRATION SCENARIO — SYNTHETIC MICRO-STATE

Use real public macro-data to anchor the scenario where possible.

Example:

```text
Real:
historical tomato arrivals + prices

Synthetic:
farmer harvest commitments
buyer capacities
processor capacities
storage capacities
transport edges
```

---

# 10. Agricultural State Model

AMIE maintains a state vector:

```text
S(t) =
[
 supply,
 demand,
 arrivals,
 inventory,
 price,
 processing_capacity,
 storage_capacity,
 transport_capacity,
 buyer_capacity,
 weather_state
]
```

Each variable has:

```text
value
timestamp
source
confidence
unit
```

Confidence is informational, not a mathematical guarantee.

---

# 11. Forecast Engine

The MVP must NOT depend on a large deep-learning model.

Start with robust baselines.

## Supply / arrivals

Preferred progression:

1. seasonal naive baseline;
2. moving average;
3. exponential smoothing;
4. Random Forest / Gradient Boosting if features justify it.

Features may include:

```text
lagged_arrivals
lagged_price
season
month
day_of_year
rainfall
temperature
production
historical_yield
```

Evaluate against time-based holdout data.

Never random-shuffle temporal forecasting data.

## Demand

For MVP:

- historical seasonal demand proxy;
- moving average;
- scenario-adjustable demand multiplier.

Example:

```text
baseline_demand × demand_multiplier
```

## Harvest timing

Use synthetic commitment windows for the first demo.

Later, derive probabilistic arrival windows from:

- crop calendar;
- historical harvest timing;
- weather/seasonal indicators.

---

# 12. Network Model

Represent agriculture as a directed time-expanded network.

Node types:

```text
FARM
MARKET
PROCESSOR
STORAGE
BUYER
PROCUREMENT
```

An edge represents a possible flow.

Each edge has:

```text
capacity
cost
travel_time
commodity
quality_constraints
time_window
```

A shipment is feasible only when:

```text
source availability
AND
destination demand/capacity
AND
transport capacity
AND
time window
AND
quality compatibility
```

---

# 13. Core AMIE Algorithm

## Step 1 — Build future state

For every future time interval:

```text
forecast supply
forecast demand
inventory
capacity
commitments
```

## Step 2 — Construct time-expanded graph

Example:

```text
Farm A @ Day 2
       |
       | 500 kg
       v
Market @ Day 2
       |
       | 300 kg
       v
Processor @ Day 3
       |
       v
Buyer @ Day 3
```

## Step 3 — Feasibility check

Use:

- max-flow/min-cost-flow;
- linear programming;
- OR-Tools;
- scipy.optimize where appropriate.

Question:

> Can all required future supply reach a valid destination within the relevant constraints?

If yes:

```text
FEASIBLE
```

If no:

```text
INFEASIBLE
```

## Step 4 — Find earliest failure

Scan future time steps.

Return:

```text
first_failure_time
failed_quantity
failed_node
failed_constraint
```

## Step 5 — Identify bottleneck

Compute capacity utilization:

```text
utilization =
actual_required_flow / available_capacity
```

Flag:

```text
> 100% = infeasible
90–100% = critical
70–90% = constrained
< 70% = available
```

Thresholds are configurable.

## Step 6 — Explain failure

Example:

```text
PROCESSOR P03

Required Day-6 intake:
4,800 kg

Available capacity:
3,100 kg

Capacity deficit:
1,700 kg

Cause:
2,400 kg of farmer commitments converge
within the same 24-hour window.
```

---

# 14. Critical Commitment Analysis

AMIE should identify a small set of future commitments whose simultaneous presence causes infeasibility.

Procedure:

1. Run full scenario.
2. If feasible, stop.
3. If infeasible, identify overloaded constraints.
4. Remove/suppress candidate commitments individually.
5. Re-run feasibility.
6. Rank commitments by reduction in infeasibility.
7. Test combinations of the top candidates.

For MVP, use greedy search rather than exponential exhaustive search.

Output:

```text
CRITICAL COMMITMENT SET

F-017  900 kg
F-024  700 kg
F-031  650 kg

Combined excess:
1,150 kg
```

Important:

The system must not claim mathematical minimality unless exhaustive/validated optimization proves it.

Use:

> “Critical set identified by heuristic search.”

---

# 15. Intervention Engine

Candidate intervention types:

### A. Redirect
Move produce to another feasible buyer/market.

### B. Reschedule
Shift flexible harvest/dispatch windows.

### C. Store
Temporarily move produce into available storage.

### D. Process
Use another processor with compatible capacity.

### E. Procurement
Activate additional procurement capacity.

### F. Route
Use an alternative transport path.

Each intervention has:

```text
intervention_id
action
affected_quantity
cost
time
farmer_disruption
capacity_effect
```

---

# 16. Intervention Optimization

Objective:

```text
minimize
    intervention_cost
  + transport_cost
  + storage_cost
  + spoilage_penalty
  + unmet_demand_penalty
  + farmer_disruption_penalty
```

Subject to:

```text
flow conservation
capacity constraints
time windows
commodity compatibility
quality constraints
inventory constraints
nonnegative flows
```

Use OR-Tools Linear Solver / SCIP where available.

If solver availability becomes problematic, implement a deterministic greedy fallback.

---

# 17. Counterfactual Simulator

Every intervention must be re-simulated.

Example:

```text
BASELINE
Processor overload: 1,700 kg
Unabsorbed produce: 1,700 kg
```

Intervention:

```text
Redirect 1,200 kg
to Processor P07
```

Re-run:

```text
Processor overload: 0 kg
Unabsorbed produce: 500 kg
```

Then second intervention:

```text
Store 500 kg
```

Final:

```text
Unabsorbed produce: 0 kg
```

---

# 18. Scenario Engine

Prebuilt scenarios:

## Scenario 1 — Synchronized harvest
Large number of farms become harvest-ready simultaneously.

## Scenario 2 — Processor outage
Reduce processor capacity by 30–70%.

## Scenario 3 — Storage shortage
Reduce available storage.

## Scenario 4 — Buyer withdrawal
Remove or reduce one major buyer.

## Scenario 5 — Transport disruption
Reduce edge capacity or disable a route.

## Scenario 6 — Demand shock
Increase/decrease buyer demand.

## Scenario 7 — Bumper harvest
Increase expected supply.

## Scenario 8 — Compound shock
Combine two or more disturbances.

Every scenario has a deterministic random seed.

---

# 19. Uncertainty

Do not pretend point forecasts are exact.

Represent forecast supply as:

```text
P10
P50
P90
```

For MVP, generate intervals using:

- historical residual quantiles;
- bootstrap;
- model prediction intervals where supported.

Run multiple scenarios across the uncertainty range.

Example:

```text
P10 supply → feasible
P50 supply → constrained
P90 supply → infeasible
```

This produces a stronger output:

> “Feasibility depends on the upper supply scenario.”

---

# 20. AMIE Risk Classification

```text
GREEN
Future feasible with available capacity.

AMBER
Feasible but critical capacity utilization is high.

RED
No feasible allocation exists under current constraints.

BLACK
No feasible allocation remains even after configured intervention options.
```

These are system states, not claims of real-world certainty.

---

# 21. Dashboard Requirements

## Page 1 — Command Center

Display:

```text
Region
Commodity
Forecast horizon
Current market state
Future supply
Future demand
System status
```

Main button:

> **RUN AMIE**

---

## Page 2 — Future Timeline

Example:

```text
DAY 1   DAY 2   DAY 3   DAY 4   DAY 5   DAY 6   DAY 7
GREEN   GREEN   GREEN   AMBER   AMBER   RED     RED
                              ^
                         FIRST FAILURE
```

---

## Page 3 — Network

Interactive graph/map:

```text
Farms → Markets → Processors → Storage → Buyers
```

Show:

- flow;
- capacity;
- utilization;
- bottleneck;
- failed route.

---

## Page 4 — Why?

Show:

```text
WHY DOES THE MARKET FAIL?

Processor P03
Required: 4,800 kg
Capacity: 3,100 kg
Deficit: 1,700 kg

Trigger:
2,250 kg arrives within same 24h window.

Current market:
HEALTHY

Future market:
INFEASIBLE
```

---

## Page 5 — Intervention Lab

Buttons:

```text
REDIRECT
STORE
RESCHEDULE
ALTERNATIVE PROCESSOR
ALTERNATIVE ROUTE
```

For each:

```text
Cost
Produce rescued
Capacity restored
Farmer disruption
Residual infeasibility
```

---

## Page 6 — Counterfactual

Side-by-side:

```text
NO INTERVENTION        AMIE INTERVENTION

Failure: YES           Failure: NO
Unabsorbed: 1,700 kg   Unabsorbed: 0 kg
Cost: ₹0               Cost: ₹X
Capacity overload: X   Capacity overload: 0
```

---

# 22. Killer Demo

Use one fixed scenario.

### Opening

```text
KERALA TOMATO MARKET
CURRENT STATUS: HEALTHY
```

Show:

```text
Supply: normal
Demand: normal
Capacity: available
```

Then:

> **SIMULATE NEXT 7 DAYS**

Timeline advances.

```text
Day 1  GREEN
Day 2  GREEN
Day 3  GREEN
Day 4  AMBER
Day 5  AMBER
Day 6  RED
```

AMIE:

> **Future infeasibility detected — 31 hours before failure.**

Click:

> **SHOW WHY**

Network reveals processor/storage bottleneck.

Then:

> **FIND CRITICAL COMMITMENTS**

AMIE identifies the synchronized farmer commitments.

Then:

> **GENERATE INTERVENTIONS**

Options appear.

Choose:

> **REDIRECT + STORE**

Re-simulate.

Final:

```text
FAILURE PREVENTED

Produce rescued: 1,240 kg
Additional infrastructure: ₹0
Intervention cost: ₹8,700
Detection lead time: 31 h
Residual overload: 0 kg
```

All numbers above are demonstration values and must be generated from the scenario, not hard-coded into claims.

---

# 23. Realism Rules

The demo must avoid fake AI magic.

Every major result needs a visible calculation path:

```text
forecast
→ quantity
→ capacity
→ constraint
→ infeasibility
→ intervention
→ re-optimization
```

Do not display:

> “AI predicts this will happen”

without supporting values.

Prefer:

> “Forecast supply exceeds feasible absorption by 1,240 kg under P90 scenario.”

---

# 24. Explainability

Each alert must expose:

```text
WHAT
WHEN
WHERE
HOW MUCH
WHY
WHAT CAUSED IT
WHAT CAN CHANGE IT
```

Example:

```text
WHAT:
Future absorption failure

WHEN:
Day 6

WHERE:
Processor P03

HOW MUCH:
1,700 kg excess

WHY:
Expected arrivals exceed processing capacity

TRIGGER:
Harvest synchronization

INTERVENTION:
Redirect 1,200 kg + store 500 kg
```

---

# 25. Technology Stack

## Backend

**Python 3.12+**

Recommended:

```text
FastAPI
Pandas
NumPy
SciPy
scikit-learn
OR-Tools
NetworkX
Pydantic
```

Optional:

```text
Statsmodels
xgboost
```

Do not add dependencies unless needed.

## Frontend

Recommended:

```text
React
TypeScript
Vite
Leaflet
Recharts
```

Alternative if frontend complexity becomes a bottleneck:

```text
Streamlit
```

For a hackathon MVP, Streamlit is acceptable and substantially faster.

## Storage

Start with:

```text
SQLite
Parquet
CSV
```

No cloud database required.

---

# 26. Recommended Build Choice

For maximum IDE-agent buildability:

```text
Python
FastAPI
SQLite
React + Vite
```

If time is severely limited:

```text
Python
Streamlit
SQLite
```

Do not build microservices.

Do not use Kubernetes.

Do not build authentication.

Do not build a payment system.

Do not build a production cloud architecture.

---

# 27. Repository Structure

```text
amie/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── external/
│   ├── synthetic/
│   └── metadata/
│       └── DATA_SOURCES.md
│
├── backend/
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── scenarios.py
│   │   ├── forecasts.py
│   │   ├── feasibility.py
│   │   └── interventions.py
│   │
│   ├── data/
│   │   ├── loaders.py
│   │   ├── validators.py
│   │   └── preprocessing.py
│   │
│   ├── models/
│   │   ├── entities.py
│   │   ├── state.py
│   │   └── forecasts.py
│   │
│   ├── network/
│   │   ├── graph.py
│   │   ├── flow.py
│   │   └── constraints.py
│   │
│   ├── simulation/
│   │   ├── scenarios.py
│   │   ├── simulator.py
│   │   └── counterfactual.py
│   │
│   ├── optimization/
│   │   ├── interventions.py
│   │   └── solver.py
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── types/
│   │   └── utils/
│   └── package.json
│
├── notebooks/
│
├── scripts/
│   ├── download_data.py
│   ├── preprocess_data.py
│   ├── generate_demo.py
│   └── train_models.py
│
└── docs/
    ├── ARCHITECTURE.md
    ├── DATA_MODEL.md
    ├── ALGORITHMS.md
    ├── DEMO.md
    └── VALIDATION.md
```

---

# 28. API Contract

## POST /scenario

Input:

```json
{
  "region": "Kerala",
  "commodity": "tomato",
  "horizon_days": 7,
  "scenario": "synchronized_harvest",
  "seed": 42
}
```

## POST /simulate

Returns:

```json
{
  "status": "INFEASIBLE",
  "first_failure_day": 6,
  "failed_quantity_kg": 1700,
  "bottleneck": {
    "id": "P03",
    "type": "PROCESSOR",
    "capacity_kg": 3100,
    "required_kg": 4800
  }
}
```

## GET /bottlenecks

Returns ranked constraints.

## POST /interventions

Input:

```json
{
  "scenario_id": "demo-001",
  "interventions": [
    {
      "type": "REDIRECT",
      "quantity_kg": 1200
    },
    {
      "type": "STORE",
      "quantity_kg": 500
    }
  ]
}
```

## POST /counterfactual

Runs baseline and intervention scenarios and returns comparable metrics.

---

# 29. Testing Requirements

Every module needs deterministic tests.

## Data tests

- units correct;
- missing values handled;
- duplicate records handled;
- dates parsed;
- quantities nonnegative;
- capacities nonnegative.

## Forecast tests

- temporal split;
- baseline comparison;
- no future leakage.

## Network tests

- flow conservation;
- capacity respected;
- time windows respected;
- impossible routes rejected.

## Feasibility tests

Construct known cases:

```text
supply 1000
capacity 1500
→ feasible
```

```text
supply 1500
capacity 1000
→ infeasible
```

## Intervention tests

```text
infeasible baseline
+
valid redirect
→ feasible
```

## Regression test

Freeze demo scenario seed:

```text
seed = 42
```

and ensure output remains stable unless intentionally changed.

---

# 30. Evaluation Metrics

## Forecasting

```text MAE
RMSE
MAPE
```

Use only when meaningful for the variable.

## Feasibility

```text failure detection accuracy
false positive rate
false negative rate
first-failure localization accuracy
```

## Intervention

```text residual unserved quantity
intervention cost
recovery percentage
transport distance
storage usage
```

## System

```text runtime
solver success rate
scenario reproducibility
```

---

# 31. Validation Strategy

Use three levels.

## Level 1 — Synthetic ground truth

Generate scenarios where the true feasible/infeasible state is known exactly.

This validates the algorithm.

## Level 2 — Historical replay

Take historical agricultural conditions and reconstruct plausible network states.

Compare predicted bottlenecks against documented or physically plausible constraints where evidence exists.

## Level 3 — Stress testing

Randomly perturb:

```text supply
demand
capacity
transport
storage
weather-derived arrival timing
```

Measure whether AMIE behaves monotonically and logically.

Example:

If capacity decreases while everything else stays equal, feasibility should not improve.

---

# 32. Invariants

These are critical.

AMIE must satisfy:

### Capacity invariant

It must never allocate:

```text flow > capacity
```

### Conservation invariant

For every node:

```text inflow + production
=
outflow + consumption + inventory_change
```

### Time invariant

Produce cannot arrive before its available date.

### Quality invariant

Produce cannot be routed to incompatible buyers/processors.

### Nonnegative invariant

No negative quantities.

### Intervention invariant

An intervention cannot magically create capacity unless its definition explicitly adds capacity.

---

# 33. LLM Usage

LLM is NOT the optimization engine.

It may be used to:

- convert numerical results into natural-language explanations;
- answer “why did AMIE flag this?”;
- summarize scenario outcomes;
- generate human-readable intervention explanations.

The LLM must receive structured results:

```json
{
  "status": "INFEASIBLE",
  "bottleneck": "P03",
  "deficit_kg": 1700,
  "trigger": "synchronized_arrivals"
}
```

It must not invent numbers.

Prompt rule:

> Only explain values contained in the supplied structured result. If a fact is absent, state that it is unavailable.

---

# 34. Agentic Coding Instructions

The IDE coding agent must follow this sequence.

## Phase 1
Create repository and data contracts.

## Phase 2
Implement synthetic scenario generator.

## Phase 3
Implement network and feasibility engine.

## Phase 4
Implement intervention optimizer.

## Phase 5
Implement counterfactual simulator.

## Phase 6
Implement public-data ingestion.

## Phase 7
Implement forecasting.

## Phase 8
Implement backend API.

## Phase 9
Implement dashboard.

## Phase 10
Integrate real data into the fixed demo.

## Phase 11
Run tests.

## Phase 12
Polish demo.

Do NOT start with UI.

The deterministic simulation core must work before visualization.

---

# 35. Agent Guardrails

The coding agent must:

- inspect existing files before modifying;
- avoid rewriting working modules unnecessarily;
- preserve API contracts;
- write tests alongside algorithms;
- use type hints;
- document non-obvious mathematical logic;
- never invent dataset fields;
- never invent API responses;
- never hard-code fake “AI predictions”;
- never silently replace a failed solver with fabricated output;
- keep synthetic and real data clearly separated;
- run tests after major changes;
- keep dependencies minimal.

---

# 36. Failure Handling

If external data download fails:

```text
use cached local dataset
```

If forecasting model fails:

```text
fallback to seasonal baseline
```

If optimizer fails:

```text
fallback to deterministic greedy allocation
```

If LLM unavailable:

```text
use template-based explanation
```

The core AMIE system must still run without an LLM.

---

# 37. Security / Reliability

Never execute arbitrary code from uploaded datasets.

Validate:

- file types;
- numeric ranges;
- units;
- schema.

No secrets committed to Git.

Use:

```text
.env
```

for optional API keys.

But MVP should require **zero API keys**.

---

# 38. Performance Target

For the demo:

- scenario generation: <1 sec;
- feasibility calculation: <2 sec;
- intervention optimization: <5 sec;
- counterfactual comparison: <10 sec;
- dashboard response: <2 sec.

These are engineering targets, not guarantees.

If the network becomes too large:

- aggregate farms;
- aggregate time intervals;
- restrict candidate routes;
- limit intervention combinations.

---

# 39. Demo Dataset Design

Create one polished synthetic scenario:

```text
Commodity: Tomato
Region: Kerala
Horizon: 7 days

Farm nodes: 30
Market nodes: 5
Processor nodes: 4
Storage nodes: 4
Buyer nodes: 8
Transport edges: ~80–150
```

Normal state:

```text
all commitments feasible
```

Injected event:

```text
harvest synchronization around Day 6
```

Result:

```text
processor P03 overload
```

Intervention:

```text
redirect + storage
```

The scenario should be seeded so every teammate gets the same result.

---

# 40. Demo Data Integrity

Do not hard-code the final numbers in frontend code.

The frontend must receive:

```text
scenario → backend → simulation → result
```

This prevents the demo from being a fake animation.

---

# 41. Definition of Done

AMIE MVP is complete only when:

- [ ] project installs from clean environment;
- [ ] no paid service is required;
- [ ] demo works offline after data preparation;
- [ ] synthetic scenario runs deterministically;
- [ ] real public data loads successfully;
- [ ] forecast module works;
- [ ] network is generated;
- [ ] feasibility is calculated;
- [ ] bottleneck is identified;
- [ ] critical commitments are identified;
- [ ] intervention is generated;
- [ ] intervention is re-simulated;
- [ ] baseline/counterfactual metrics are displayed;
- [ ] all quantities obey physical constraints;
- [ ] tests pass;
- [ ] source/licensing metadata is documented;
- [ ] synthetic data is visibly labelled;
- [ ] demo can be completed in under 3 minutes.

---

# 42. Final Product Boundary

AMIE is NOT:

```text
a farmer marketplace
a price-prediction app
a generic agricultural chatbot
a satellite crop-health classifier
a generic digital twin
a generic supply-chain optimizer
a generic disaster predictor
```

AMIE IS:

> **A future agricultural feasibility engine that reconstructs expected supply/demand/capacity commitments, detects when the resulting system becomes physically infeasible, identifies the constraint and critical flows responsible, and calculates counterfactual interventions that restore feasibility.**

---

# 43. Final Demo Narrative

The evaluator sees:

```text
CURRENT MARKET
HEALTHY
```

Then:

```text
SIMULATE FUTURE
```

AMIE reveals:

```text
DAY 6
FUTURE INFEASIBILITY
```

Then:

```text
WHY?
```

The network exposes the physical bottleneck.

Then:

```text
WHAT CAUSED IT?
```

AMIE identifies synchronized commitments.

Then:

```text
WHAT CAN WE DO?
```

AMIE generates interventions.

Then:

```text
SIMULATE INTERVENTION
```

The impossible future becomes feasible.

The product's central proof is:

> **AMIE does not merely predict that agricultural conditions may worsen. It demonstrates that a specific future state is physically infeasible, explains why, and computes a feasible alternative.**
