---
name: trello-project-sync
description: Synchronizes project tasks between the AI Agent's state store and Trello boards using a perceive-plan-act-evaluate loop.
---

# Trello Project Sync Skill

This skill enables the `AgentOrchestrator` to manage project workflows by mapping agentic state to Trello's Kanban structure (Boards $\rightarrow$ Lists $\rightarrow$ Cards).

## Tech Stack Alignment
- **Primary:** TypeScript, Node.js (executed via Cloudflare Functions).
- **Orchestration:** AgentOrchestrator (`core/ai_agent.py`).
- **Integration:** Trello REST API, `core/state.py` for local state persistence.

---

## Execution Phases

### Phase 1: Diagnosis (Perceive)
The agent audits the current state of the Trello board vs. the local state store.
- **Board Audit:** Fetch all lists and cards from the target Trello board.
- **State Comparison:** Compare the local `state.json` (containing current tasks and progress) with Trello card titles and labels.
- **Gap Analysis:** Identify "orphaned" cards (on Trello but not in state) and "missing" cards (in state but not on Trello).

### Phase 2: Analysis (Plan)
The agent determines the necessary mutations to synchronize the two systems.
- **Mapping Strategy:** 
    - Map "To Do" state $\rightarrow$ "Backlog" list.
    - Map "In Progress" state $\rightarrow$ "Doing" list.
    - Map "Completed" state $\rightarrow$ "Done" list.
- **Mutation Queue:** Create a prioritized list of API calls: `CREATE_CARD`, `MOVE_CARD`, `UPDATE_CHECKLIST`.
- **Constraint Check:** Verify Trello API Key and Token are present in `.env`.

### Phase 3: Programming & Execution (Act)
The agent executes the synchronization plan using the Trello API.
- **Card Orchestration:**
    - Create cards for new tasks identified in Phase 1.
    - Move cards between lists based on state transitions (e.g., moving a task to "Done" upon verification).
- **Detail Enrichment:** 
    - Inject task descriptions and checklists into Trello cards.
    - Add labels (e.g., "AI-Generated", "High Priority") to categorize work.
- **Persistence:** Update the local `StateStore` with Trello Card IDs for future direct reference.

### Phase 4: Verification (Evaluate)
The agent validates that the board accurately reflects the project state.
- **Visual Audit:** Re-fetch the board to ensure all mutations were applied.
- **Consistency Check:** Verify that no duplicate cards were created.
- **Report:** Generate a synchronization summary (e.g., "5 cards created, 2 moved, 0 errors").
