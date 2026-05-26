# Memory Workflow

Purpose:

- Preserve durable project context across context compaction and new sessions.
- Avoid relying only on chat history for scene state, decisions, and next steps.

Canonical location:

- `C:\Users\egork\Desktop\coppelia_dpilom`

How to resume:

1. Read [[00_INDEX]].
2. Read [[01_CURRENT_STATE]].
3. Read [[03_TASKS]].
4. Read relevant linked notes, especially [[final_scene_palletizing_cycle]].
5. Continue from the next listed task, checking the current CoppeliaSim scene before editing.

When starting Codex, open the project folder `C:\Users\egork\Desktop\coppelia_dpilom` as the workspace.

During work:

- Update [[01_CURRENT_STATE]] after significant scene/script changes.
- Update [[03_TASKS]] when task status or next steps change.
- Update [[02_DECISIONS]] for durable design choices.
- Add a concise entry to the daily log.

If context compaction happens mid-task:

- Do not restart from scratch.
- Read [[00_INDEX]], [[01_CURRENT_STATE]], and [[03_TASKS]].
- Check the latest daily log.
- Inspect actual files/scene state before continuing.
- If memory and current scene disagree, mark it as an open question in [[01_CURRENT_STATE]] and verify through CoppeliaSim/ZMQ.
