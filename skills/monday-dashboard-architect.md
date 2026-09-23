---
name: Monday Dashboard Architect
description: Designs and implements high-level operational dashboards in Monday.com for business intelligence and KPI tracking.
---

# Monday Dashboard Architect

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Stakeholder Interview**: Identify the key metrics (KPIs) the dashboard must track.
- **Data Source Audit**: Review existing Monday.com boards, columns, and data structures.
- **User Persona Mapping**: Determine who will use the dashboard (Execs, Project Managers, Ops) and their specific needs.
- **Gap Analysis**: Identify data that is missing from Monday.com but required for the dashboard.

### 2. Analysis (Plan)
- **Information Architecture**: Group KPIs into logical sections (e.g., Financials, Velocity, Risk).
- **Widget Selection**: Map metrics to Monday.com widgets (Battery, Chart, Numbers, Gantt).
- **Data Flow Design**: Plan the use of "Connect Boards" and "Mirror Columns" to aggregate data from multiple boards into a single source of truth.
- **Filter Specification**: Define the necessary dashboard filters (e.g., by Date, by Department, by Status).

### 3. Programming (Act)
- **Board Optimization**: Adjust board structures, add necessary status columns, and configure mirroring.
- **Dashboard Construction**:
    - Create the dashboard and implement the planned widgets.
    - Configure complex formulas in Monday.com to calculate custom KPIs.
- **Automation Setup**: Implement Monday.com automations to keep data updated (e.g., "When status changes to Done, move item to Archive board").
- **API Extension**: If native widgets are insufficient, develop a custom Monday app using Node.js/TypeScript to fetch and visualize data.

### 4. Verification (Evaluate)
- **Data Accuracy Audit**: Compare dashboard numbers against raw board data to ensure formula correctness.
- **Usability Testing**: Conduct a walkthrough with stakeholders to ensure the layout is intuitive.
- **Performance Check**: Verify that the dashboard loads efficiently despite large data volumes.
- **Feedback Loop**: Implement a versioning process for iterative improvements based on user feedback.