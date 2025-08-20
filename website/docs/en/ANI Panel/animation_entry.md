---
title: Animation Entry
order: 8
---

## Entries
The table contains entries of imported animation. The icon indicate whether the animation sourced from animation file, or retargeted animation, followed by name, and total keyframes correlate to project/scene FPS (unless [`Use Scene Fps`](#use-scene-fps) is disabled, it will recalculate keyframe amount based off the FPS input)

This entry is project dependant, the entries cannot be transferred from one project to another through `File > Link/Append`, but can be exported into `ANI` or `JSON`.

After entry is selected, use the [`Apply Animation`](#apply-animation) operator to append them to selected empty/armature. It doesn't matter which bone you choose, as long the skeleton was imported using advanced mode.

### Entry: Import
Operator to import animation, which then will be append to entries.

!!! tip "Multi-file support"
    This operator support processing multiple files at once. Simply select all files you want to import, and then the script will import all of them individually.

### Entry: Delete
Operator to delete animation entry. The current selected entry will be removed.

### Entry: Export
Operator to export entry into `.json`, intended for retarget. To export animation from skeleton, use [`Export Animation`](../ANI%20Panel/export_animation.md) instead

___

## Settings
### Use Scene FPS
Whether to use project FPS, or user defined FPS to calculate keyframes for animation.

### Frame Range
If set to partial, then imported animation will only apply animation within this range only.

!!! failure "Known Issue"
    This setting is currently broken. Due to recent change on [`Apply Animation`](#apply-animation) operator, this setting will cause error if set to `Partial`. Unfortunately I do not know how to fix this.

### Frame Insert
Setting to define where to insert keyframe, can be either: current frame, first frame, or user defined frame.

___

## Apply Animation
Append animation from selected entry into selected skeleton. It doesn't matter which bone you choose, as long the skeleton was imported using advanced mode.

!!! warning "Known Issue"
    Due to [recent change](https://github.com/Trisnox/lost-saga-io3d/commit/bcbef8def8d51ae8ff7bba2861d6bdff48da444b#diff-651b52dc7bdcd71d8763d2391f20df4d18e8b3f94b234d13186e8a70d6de9125), the keyframe insertion method for `Apply Animation` has been improved, as this is much faster compared to previous version. However, the catch is that partial frame range is no longer possible, and apply animation in between keyframes will also cause error.

    In order to work around this, simply apply animation after the last keyframe, delete keyframe(s) if you only need partial, and then drag them to your desired frame.