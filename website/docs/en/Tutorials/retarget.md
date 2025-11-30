---
title: "Retarget Animation"
---

Retarget involves the process of copying animation sourced from other armature, into another armature. While it might sounds simple, it's not the case with Lost Saga skeleton due to how their skeleton are formed. However, there is such addon that allows us to retarget animation properly.

## Installing the addon
You need to [install this addon first](https://extensions.blender.org/add-ons/bone-animation-copy-tool/)

!!! warning "Addon Support"
    Since I am not the creator/owner of the addon, please do not ask me for assistance.


## Importing the Skeleton
[Import skeleton using advanced mode](../SKL%20MSH%20Panel/skeleton_import.md) with using `Armature` as its display.


## Matching source/target
Assuming that you had imported the target armature, use losa skeleton as the source, and the target to copy animation from.

![source target armature](../images/source_target.png)


## Configuring Bones

!!! info "MMD Skeleton"
    If you're using mmd skeleton, there exist [pre-configured mapping for mmd skeleton](../sample_files.md#mmd-bones-preset)

Select both armature, and then enter pose mode. After that, you can map the bones to copy animation from, as well fixing the rotation offset for each bone. Once you're done, it should looked like this more or less

![mapping](../images/mapping.png)


## Final Result
After fixing the rotation, you can bake the animation and then [export them into `.ani`](../ANI%20Panel/export_animation.md)

![type:video](../videos/retarget_result_new.mp4)

!!! info "Animation"
    You can get the exported animation file [here](../sample_files.md#mmd-retarget-animation)