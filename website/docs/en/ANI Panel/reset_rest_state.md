---
title: Reset Rest State
order: 3
---

This operator is only for advanced skeleton only.

## Reset Rest State
Reset selected bones to its rest position and rotation.

!!! info "Initial Rotation"
    Here is what Lost Saga skeleton initial position/rotation looked like.

    It doesn't resemble anything like humanoid at all, the humanoid form is actually stored inside [`LocalTMqRot` or `kObjectMatrix`](../binary_structure.md#biped). However, this initial rotation is still needed because animation quaternion calculate their rotation from this initial position, instead of rest rotation from humanoid
    
    ![losa skeleton](../images/losa_weird_skeleton.png)
