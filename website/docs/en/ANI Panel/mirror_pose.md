---
title: Mirror Pose
order: 2
---

This operator is only for advanced skeleton only.

## Mirror Pose
Mirror pose of the selected bones to the opposite bones. Depending on the [Mirror Target](#mirror-target), this will either copy the pose from opposite bone, or to mirror selected bones pose to the opposite. Does nothing if the bone have no symmetrical counterpart. Works for both Blender and Lost Saga bone names. This is equivalent to [Paste Pose Flipped](https://docs.blender.org/manual/en/latest/animation/armatures/posing/editing/copy_paste.html)

## Mirror Target
Operation used for [Mirror Pose](#mirror-pose).

- `Mirror Opposite Bones`: Copy pose from selected bones, and then paste them to the opposite
- `Copy Opposite Bones`: Copy pose from opposite bones, and then paste them to the selected bones

!!! info "Mirror Target"

    === "Mirror Opposite Bones"
        ![mirror_pose](../images/mirror_pose_mirror.png)

    === "Copy Opposite Bones"
        ![mirror_pose](../images/mirror_pose_copy.png)

## Location/Rotation Checkbox
When either box is unchecked, then location/rotation will not be mirrored