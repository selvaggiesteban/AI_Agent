---
name: monday-automation-orchestrator
description: Automates project tracking on Monday.com by synchronizing agentic workflows with boards, items, and columns.
---

# Monday Automation Orchestrator

This skill allows the `AgentOrchestrator` to leverage Monday.com as a Work OS for tracking the execution of complex, multi-phase agentic tasks.

## Tech Stack Alignment
- **Primary:** TypeScript, Node.js (executed via Cloudflare Functions).
- **Orchestration:** AgentOrchestrator (`core/ai_agent.py`).
- **Integration:** Monday.com GraphQL API, `core/state.py`.

---

## Execution Phases

### Phase 1: Diagnosis (Perceive)
The agent audits the Monday.com board structure and current item statuses.
- **Schema Audit:** Fetch board columns to identify status markers (e.g., "Status", "Priority", "Owner").
- **Item Scanning:** Retrieve all items and their current column values.
- **Alignment Check:** Match Monday items to the active tasks in the agent's `StateStore`.

### Phase 2: Analysis (Plan)
The agent plans the updates required to reflect current progress.
- **Update Mapping:**
    - Map "Planned" tasks $\rightarrow$ "Working on it" status.
    - Map "Verified" tasks $\rightarrow$ "Done" status.
- **Automation Trigger:** Plan for the creation of new items if the agent discovers new sub-tasks during the "Perceive" phase of other skills.
- **Credential Validation:** Ensure `MONDAY_API_TOKEN` is available in `.env`.

### Phase 3: Programming & Execution (Act)
The agent executes the GraphQL mutations to update the board.
- **Item Management:**
    - `create_item`: Add new tasks discovered by the agent.
    - `change_column_value`: Update status and priority columns.
- **Context Injection:** Update the "Updates" section of a Monday item with the latest evaluation reports from the `Evaluate` phase of the reasoning loop.
- **User Notification:** Use Monday's notification system to alert the user of critical blocks or completed milestones.

### Phase 4: Verification (Evaluate)
The agent verifies the board state.
- **GraphQL Query:** Re-query the board to ensure the `change_column_value` mutations were successful.
- **State Sync:** Confirm that the local `StateStore` now reflects the Monday.com item IDs.
- **Consistency Report:** Output a summary of items updated and any API errors encountered.
