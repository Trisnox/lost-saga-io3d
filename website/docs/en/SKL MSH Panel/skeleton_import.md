---
title: Skeleton Import
order: 1
---

## Import Skeleton
You can import skeleton files (`.skl`) through io3d n-panel, inside `SKL/MSH` panel > Import Skeleton, or through `File > Import > Lost Saga Skeleton (.skl)`

Usually, you'd want to import `normal.skl` for humanoid skeleton

!!! warning "Warning"

    Do not remove `origin_correction` bone in any way. This bone is crucial to fix coordinate system differences. Without this, animation might be broken. It's safe to remove the bone if it were imported using lite.

    Do not apply transformation either, it will break bone rotation.

    If you want to reset the bone rotation to its rest position, use [`Reset Rest Position`](../ANI%20Panel/reset_rest_state.md) instead. Unless you're using lite/legacy bone, there is no need to use the operator, use `alt+r` to reset rotation instead.

## Modes
From here you can choose various mode depending on what you need.

![skl modes](../images/skl_modes.png)

- Lite: If you only need the skeleton to weight paint, or to do animation (not for import/export), you should choose this. This skeleton is formed in same way like advanced does, minus the mesh armature, and the transformation are applied
- Advanced: This mode allows for pretty much almost everything, mainly import/export animation
- Retarget: Currently broken, can be used, but result are nowhere near perfect. This bone is intended to be used for retarget, use this armature as the target, at which you can use [Retarget Animation operator](../ANI%20Panel/retarget_animation.md), this retargeted animation entry can be later exported, and then applied to advanced skeleton
- Legacy: Bones formed using LocalTMvPos/ObjectTMvPos. Use lite/advanced instead

## Display

### Empty
Recommended display

![empties display](../images/display_empty.png)

### Armature
Not recommended due to offset issue, but they will work fine regardless

![armature display](../images/display_armature.png)

!!! info "Comparison"

    Comparison of both display. **Using armature does not affect the final result when exported**

    ![offset comparison](../images/offset_comparison.png)