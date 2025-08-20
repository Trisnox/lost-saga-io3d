---
title: ANI Panel
---
# Overview

![ani panel](../images/ani_panel.png)

Do note that most of operator here only works for advanced skeleton.

## Animation Utility
- Flip Pose: Flip pose, affect entire bones
- Mirror Pose: Mirror pose, can either copy from opposite, or mirror to opposite
- Reset Rest State: Reset the bone rotation to its rest state
- Mirror Target: Used for mirror pose, it can be set to copy or mirror
- Location/Rotation checkbox: Used for mirror pose, exclude either location or rotation for mirroring
- Swap Armature Display: Swap between empty or armature display
- Remap Frames: Remap keyframe timing, only work if user is using `Output > Frame Range > Time stretching`

## Animation
- Export Animation: Export animation into `.ani`. Only works for advanced skeleton
- Apply Delta Transformations: Used for retarget. Apply delta transformations to all selected object and its animation data

## Animation Entry
- Entry: All imported animation will be listed in this entries
- Import Animation: Import `.ani` file or `.json`
- Delete: Delete animation entry
- Export: Export animation entry into `.json` file
- Use Scene FPS: When enabled, imported animation timing will use current FPS to append keyframes, otherwise user can set their own FPS value
- Frame Range: Number of keyframes to append, if set to all, then all keyframes will be applied, otherwise only partial amount will be appended
- Frame Start/End: Used for frame range, if using partial. Limit keyframe only to these range only
- Frame Insert: Offset to define where the keyframe should be appended
- Apply Animation: Append animation to selected armature