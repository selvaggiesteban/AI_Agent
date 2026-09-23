---
name: Operational Bottleneck Analyzer
description: Uses data-driven analysis to identify and resolve inefficiencies in business processes and workflows.
---

# Operational Bottleneck Analyzer

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Process Documentation**: Map the "as-is" process using a flow chart or BPMN diagram.
- **Data Collection**: Gather timestamps for each step of the process (e.g., from Trello, Jira, or custom logs).
- **Stakeholder Feedback**: Interview team members to identify "invisible" bottlenecks (e.g., waiting for approval).
- **KPI Baseline**: Define the current cycle time and lead time.

### 2. Analysis (Plan)
- **Quantitative Analysis**:
    - Calculate the "Waiting Time" vs. "Processing Time" for each step.
    - Identify the "Constraining Resource" (the person or system that limits throughput).
- **Root Cause Analysis**: Use "5 Whys" or Ishikawa diagrams to find why the bottleneck exists.
- **Hypothesis Generation**: Propose 2-3 interventions (e.g., "Automate step X", "Add a second reviewer").
- **Impact Prediction**: Estimate the reduction in cycle time for each proposed solution.

### 3. Programming (Act)
- **Intervention Implementation**:
    - Deploy the proposed automation (using the relevant automation skill).
    - Reconfigure the process flow (e.g., moving from sequential to parallel approval).
- **Monitoring Setup**:
    - Implement a tracking system (e.g., custom DB logs or Monday.com dashboards) to measure the change.
    - Set up alerts for when a card/task exceeds the expected time in a specific stage.

### 4. Verification (Evaluate)
- **Post-Intervention Analysis**: Compare the new cycle time and lead time against the baseline.
- **Throughput Measurement**: Verify if the total number of completed units per period has increased.
- **Secondary Effect Audit**: Check if the bottleneck simply shifted to another part of the process.
- **Iterative Refinement**: Adjust the intervention based on the data and repeat the cycle.