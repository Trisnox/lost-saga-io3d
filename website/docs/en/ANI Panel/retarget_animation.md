---
title: Retarget Animation
order: 6
---

This operator is only for retarget skeleton only.

## Retarget Animation
Export animation as animation entry, which then can be exported into `.json`, and applied to Lost Saga Skeleton. Retargeted animation have different icon, which indicates that they're sourced from retarget.<br>
Depending whether [`Apply Rest Rotation`](./animation_entry.md#apply-rest-rotation) is enabled or not, retarget animation will try to multiply its quaternion with rest quaternion.

!!! failure "Warning"
    Retargeting is currently nowhere near good or perfect, attempting to do so will not produce any doable results.

    The current proposed solution is to use [delta transformation](https://docs.blender.org/manual/en/latest/scene_layout/object/editing/apply.html#transforms-to-deltas) [(another explanation)](https://blenderartists.org/t/object-apply-all-transforms-vs-all-transforms-to-deltas/1327289) for retarget, which stores its rest rotation without having to modify its initial rotation. We then can calculate the position/rotation based off current position/quaternion and then added/multiplied by its delta position/quaternion.