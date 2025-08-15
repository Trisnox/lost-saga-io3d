---
title: Exporting Animation
---

Exporting animation is relatively simple, however, you need certain skill of animating to be able to create decent animation. Either way, to export animation, you simply need to use [advanced skeleton](../SKL%20MSH%20Panel/skeleton_import.md), the display and which bone you choose doesn't matter, the script will read the animation data from the empties collection if it was using empty display, or the armature itself if it was using armature display. Optionally, you can also attach mesh, use the `mesh_armature` object to attach mesh with. This armature is specifically made for meshes.

Using either display is up to your choice, both will work the same, and both have same export result. Though, keep in mind that armature display have [offset issue](../SKL%20MSH%20Panel/skeleton_import.md#armature), but it will not affect the final result.

!!! warning "One display at a time"
    Even though you can swap armature display at any time, the script does not transfer animation data upon switching. So you should stick to only either display. You could however, transfer the animation data by using [`bake action`](https://docs.blender.org/manual/en/latest/editors/nla/editing/strip.html#bpy-ops-nla-bake) since both display constraints each other.

## Exporting Animation
Just simply import advanced skeleton, and you can start animating on the skeleton. You can also import mesh to see how the animation will looked like on mesh.

There are also [numerous operator](../ANI%20Panel/index.md) to help with animating, you should use these operator instead of built-in operator due to Lost Saga skeleton have weird bone initial rotation. The operator works for both Lost Saga or Blender bone names if you use [rename bones operator](../SKL%20MSH%20Panel/rename_bones.md), though it's not recommended since there is little usage to renaming advanced skeleton.

Since [`.ani` only contains location and rotation](../binary_structure.md#tracks), any other keyframe (like scale), will be ignored.

!!! tip "Interpolation"
    Unfortunately, Lost Saga always interpolate their keyframes using linear interpolation. If you have any other inpterpolation other than linear in one of your keyframe, you should [`bake`](https://docs.blender.org/manual/en/latest/editors/nla/editing/strip.html#bpy-ops-nla-bake) your armature first before exporting. This will bake the inbetween in correlation with the interpolation it uses.

!!! info "Keep location consistent"
    When animating, you should always try to keep the location of the bones to be consistent. It's okay to move the root (not `origin_correction`) or pelvis bone, but any other bone position should not be altered, unless you wanted to do funky deformation with certain bones.

![type:video](../videos/animating.mp4)

!!! tip "Sample Files"
    Still confused? check the [sample files here](../sample_files.md).