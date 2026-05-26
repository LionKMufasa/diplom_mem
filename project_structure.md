# Project Structure

Canonical root:

- `C:\Users\egork\Desktop\coppelia_dpilom`

Folders:

- `scenes/` - CoppeliaSim `.ttt` scenes.
- `scripts/coppeliasim/lua/` - Lua scripts installed into scenes.
- `scripts/coppeliasim/python/` - Python/ZMQ helper and installer scripts.
- `data/telemetry/` - CSV telemetry logs.
- `data/reports/` - JSON reports from simulation/IK/dynamics checks.
- `models/` - robot model assets and future trained ML model artifacts.
- `models/coppeliasim/` - CoppeliaSim model files such as `.ttm`.
- `models/solidworks/` - SolidWorks and STEP source CAD files.
- `models/ros_urdf/` - ROS/URDF exports with meshes and launch/config files.
- `docs/rpz/` - future RPZ/report text and source documents.
- `docs/nirs8_rpz/` - NIRS-8 report planning notes and working structure.
- `docs/presentations/` - presentation planning notes for NIRS/VKR decks.
- `docs/project_deliverables_plan.md` - VKR/NIRS deliverables map and chat split plan.
- `reports/` - rendered reports, figures, exported results.
- `experiments/` - future ML/simulation experiment runs.
- `assets/` - external assets and prepared source materials.
- `logs/` - Markdown work log by date.

Root Markdown memory:

- `00_INDEX.md`
- `01_CURRENT_STATE.md`
- `02_DECISIONS.md`
- `03_TASKS.md`
- `04_USER_PREFERENCES.md`
- `memory_workflow.md`
- `final_scene_palletizing_cycle.md`
- `project_structure.md`

Copied legacy/project files:

- Scenes are stored in `scenes/`.
- Main Lua scripts copied from `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu` into `scripts/coppeliasim/lua/`.
- Python helper scripts copied into `scripts/coppeliasim/python/`.
- Existing CSV telemetry stored in `data/telemetry/`.
- Existing JSON reports copied into `data/reports/`.
- Robot model files moved into `models/coppeliasim`, `models/solidworks`, and `models/ros_urdf`.

Note:

- Top-level duplicate `.ttt` and `.csv` files were removed after hash verification. Prefer structured folders for all new work.
