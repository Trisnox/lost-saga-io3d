---
title: Apply Delta Transforms
order: 6
---

This operator is only for retarget skeleton only.

## Apply Delta Transforms
Apply delta transformation into all selected objects and its animation data. After applying delta, animation can be exported using [`Export Animation` operator](./export_animation.md)

[Guide for retargeting also exists](../Tutorials/retarget.md).

!!! bug "Known Issue"
    This operator only works for position and rotation only, and as long they have animation data into it. If the objects does not contain either data, just simply re-bake the actions with both position and rotation applied

!!! failure "Warning"
    Retargeting is currently nowhere near good or perfect, attempting to do so will not produce any doable results. Unfortunately, I have lost motivation to continue retarget. Working with Lost Saga skeleton is already enough as is due to weird skeleton they had. The current retarget is capable of accurately mimicking the rotation of all bones but legs and with twists on some bones.