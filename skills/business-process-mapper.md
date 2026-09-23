---
name: Business Process Mapper
description: Visualizes and documents complex business operations to identify redundancies and optimize efficiency.
---

# Business Process Mapper

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Stakeholder Interviews**: Conduct workshops with "process owners" to document how work actually gets done.
- **Artifact Collection**: Gather existing manuals, checklists, and informal "how-to" docs.
- **Observation**: Shadow employees to identify the "shadow processes" (workarounds not in the official docs).
- **Tooling Audit**: List every piece of software used in the process (e.g., "Email -> Spreadsheet -> Trello -> Stripe").

### 2. Analysis (Plan)
- **Process Decomposition**: Break the high-level process into sub-processes and individual steps.
- **Logic Mapping**: Identify decision points (Yes/No branches) and loops.
- **Symbol Selection**: Choose a mapping standard (e.g., BPMN 2.0) for clarity and professionalism.
- **Critical Path Identification**: Determine the sequence of steps that directly impacts the final delivery time.

### 3. Programming (Act)
- **Visual Mapping**:
    - Create the process map using a tool like Mermaid.js (for version control) or LucidChart.
    - Document the inputs, outputs, and owners for every step of the map.
- **Documentation**: Write a technical guide explaining the logic, exceptions, and "happy path" of the process.
- **Optimization Proposal**: Highlight the "redundant loops" and "manual hand-offs" on the map with a heat-map overlay.

### 4. Verification (Evaluate)
- **Validation Session**: Walk through the map with the team to ensure it accurately reflects reality.
- **Gap Analysis**: Compare the "As-Is" map with the "To-Be" optimized version.
- **User Testing**: Give the documentation to a new employee and see if they can execute the process without help.
- **Maintenance Plan**: Establish a cadence for reviewing and updating the map as the business evolves.