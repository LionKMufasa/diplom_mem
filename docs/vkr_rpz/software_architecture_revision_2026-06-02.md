# VKR RPZ Software And Architecture Revision - 2026-06-02

## Context

The teacher asked to clarify two points in the VKR RPZ:

- justify the software choice, especially around table 6;
- describe the practical path of preparing the robot model: STEP model download, SolidWorks assembly/constraints setup, URDF export, and CoppeliaSim import/tuning.

The user clarified that the detailed digital-model preparation story should remain in chapter 5, as originally planned. Chapter 2 should first justify the software stack and only after that describe the architecture.

## Accepted Revision Plan

Chapter 2 should be reorganized as:

1. `2.1. Цель и задачи проектирования`
2. `2.2. Обоснование выбора программных средств`
   - table 6 becomes `Таблица 6 - Обоснование выбора программных средств`;
   - table 6 compares selected tools with alternatives and states limitations.
3. `2.3. Общая архитектура ПАК`
   - architecture is described after software justification;
   - architecture table should describe logical system levels, not duplicate software choices.
4. `2.4. Функциональная модель и потоки данных`
5. `2.5. Анализ архитектурного варианта`
   - table 8 should be an architecture-variant comparison, not a repeated technology-stack table.
6. `2.6. Формирование требований к системе`
7. `2.7. Выводы по главе`

## Table Role Separation

- Table 6: why these software tools were chosen.
- Table 7: which logical levels form the PAK architecture.
- Table 8: why the selected architecture variant is appropriate.

## Chapter 5 Addition

Chapter 5 should include a detailed working-design passage about preparing the digital model:

- a STEP model of the robot was found/downloaded;
- STEP preserved geometry but not a ready controllable simulation model;
- SolidWorks was used to restore/check assembly relations, joint axes and relative link positions;
- the model was exported to URDF;
- URDF carried the link/joint hierarchy into CoppeliaSim, but did not remove the need for manual tuning;
- CoppeliaSim required manual hierarchy cleanup, drive/joint setup, dummy/closure links, scene objects, working-cycle tuning and trajectory calibration;
- leave a signed placeholder for one future SolidWorks screenshot.

## Numbering Requirements

After editing, check and, if needed, renumber:

- table captions and references in text;
- figure captions and references in text;
- formula captions and references in text.

