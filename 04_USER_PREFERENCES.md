# User Preferences

Last updated: 2026-05-06

## Simulation Workflow

- Work directly in the currently running CoppeliaSim scene when the user says it is running.
- Connect through ZMQ and inspect the actual scene before changing scripts.
- Do not assume older scenes (`Diploma`, `test2`, `test1`) match the current one.
- Preserve user-created scene objects and manual fixes unless explicitly told otherwise.

## Palletizing Semantics

- Cardboard and bottle/water bundles must not be confused.
- A "cube" in the cycle means 7 thermal packs with 6 bottles of 1.5 L water each, total mass about `63 kg`.
- Cardboards are separator sheets/layers.
- Objects should be generated where their source/template objects initially stand in the scene.
- Robot should visibly move close to objects before pickup; avoid picking "from the air".

## Reporting

- Prefer concise Russian updates with concrete file paths and verification results.
- Mention exact scene and script names when changes are made.
- Keep durable project facts in Markdown memory without asking extra permission.
- For NIRS-8 literature references, use one source number per bracket, for example `[9]`; avoid grouped citations such as `[9, 18]`.

## Project Memory

- Maintain the external Markdown project memory in the current project folder.
- At the start of work, read [[00_INDEX]] and [[01_CURRENT_STATE]].
- After significant changes, update [[01_CURRENT_STATE]], [[03_TASKS]], and when relevant [[02_DECISIONS]] plus `logs/YYYY-MM-DD.md`.
- Store only durable facts, decisions, constraints, and next steps; do not duplicate the chat.
- Use wikilinks for new important project entities and notes.
- If chat context conflicts with memory files, clarify or mark the conflict as an open question in [[01_CURRENT_STATE]].

## VKR RPZ Workflow

- Work in Russian in the file `ВКР\ВКР 2026 Миронов Егор Максимович.docx`.
- Fill the VKR RPZ DOCX directly by default, including large chapter text.
- Ready-to-insert chat text is still acceptable when the user explicitly asks to review text before insertion.
- Build the VKR presentation only after the RPZ is substantively ready.
- It is acceptable to reuse suitable text and figures from NIRS-7, but the VKR should be expanded and adapted rather than pasted mechanically.
- Prefer concrete verification notes for DOCX edits: structural audits, TOC status, render/PDF limitations, and exact file paths.
