---
title: Export Animation
order: 7
---

This operator is only for advanced skeleton only.

## Export Animation
Export animation from active armature or empties collection. Empties collection simply only need one to be selected, the script will automatically select all bone based on topmost parent. The resulting file is `.ani`

!!! tip "Adding Events"

    By default, animations exported using this add-on is empty, you can add events using the [`Events Editor`](../events_editor.md) script.

!!! info "Limitation and Workaround"

    Lost Saga animation can have more than one armature object across single file. Currently, the script does not support this kind of behaviour. Instead, what you should do is to merge the armature together, this way the script will export all animation from each bones accordingly. Just make sure to parent the root bone to `origin_correction`, since that bone is used as a base parent. Do note that any bones starting with `origin_correction` name will be skipped, as they're only exist to fix rotation of the armature while retaining original coordinate system.

    Proposed solution for this problem is to read all bones from all selected objects.

!!! info "Empty vs Armature"

    [As stated previously](../SKL%20MSH%20Panel/skeleton_import.md#armature), using either display will not affect export result. It is a matter of preference whether you're much more comfortable animating using empties object, or armature object. [The sample file even uses the armature display](../sample_files.md#animation), but the final result is unaffected.

    Using armature display does have offset issue, unfortunately this cannot be fixed. This is because the armature uses both rotation and position in pose mode, which cause the armature to appear 2x larger. The armature was scaled down by half to match the humanoid model and cannot have their position reset, otherwise the export result will be broken.