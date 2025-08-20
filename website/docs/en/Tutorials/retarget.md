---
title: "[Not Working] Retarget Animation"
---

!!! failure "Warning"
    Retargeting is currently nowhere near good or perfect, attempting to do so will not produce any doable results. Unfortunately, I have lost motivation to continue retarget. Working with Lost Saga skeleton is already enough as is due to weird skeleton they had. The current retarget is capable of accurately mimicking the rotation of all bones but legs and with twists on some bones.

!!! warning "warning"
    Retarget does not support retargeting position due to how Lost Saga skeleton are formed. Forcing position will make the result worse than it was.

Retarget involves the process of copying animation sourced from other armature, into another armature. While it might sounds simple, it's not the case with Lost Saga skeleton due to how their skeleton are formed.

!!! info "Initial Rotation"
    Here is what Lost Saga skeleton initial position/rotation looked like.

    It doesn't resemble anything like humanoid at all, the humanoid form is actually stored inside [`LocalTMqRot` or `kObjectMatrix`](../binary_structure.md#biped). However, this initial rotation is still needed because animation quaternion calculate their rotation from this initial position, instead of rest rotation from humanoid
    
    ![losa skeleton](../images/losa_weird_skeleton.png)

Fortunately, I have create a solution to retargeting, even though it's not perfect.

## Importing the Skeleton
First, [import skeleton using retarget mode](../SKL%20MSH%20Panel/skeleton_import.md), at which your skeleton should looked like this:

![retarget skeleton](../images/retarget_armature.png)

It contains two skeleton, armature and empties. The armature are used for retarget animation, while the empties are used to export the animation.

## Retargeting the Animation
Use the armature as the target armature for the retaget, you should adjust source armature to match with the target armature. After retargeting, the empties will copy the rotation from the retarget armature.

![type:video](../videos/retargeting_animation.mp4)


## Exporting Retarget
After animation has been properly retargeted, select all empties, and then bake action (`F3` > Bake Action). Make sure that `Visual Keying` and `Clear Constraints` is enabled.

![bake action](../images/bake_action.png)

After baking, use the [`Apply Delta Transforms` operator](../ANI%20Panel/apply_delta.md), and then you can export them using [`Export Animation` operator](../ANI%20Panel/export_animation.md).

## Final Result
You can use the newly `.ani` file to the advanced skeleton to see and/or tweak the result before exporting to game. As stated previously, the final result is not good.

![type:video](../videos/retarget_result.mp4)