---
title: Export Collision
order: 1
---

## Export Collision
Export active mesh object as collision mesh files (`.cms`).

Exporting mesh will automatically convert the coordinate difference and triangulate the mesh, so there is no need to rotate or triangulate the mesh beforehand.

[Collision only contains vertex and face indices](../binary_structure.md/#cms).

!!! info "Face Orientation"
    Make sure that [face are oriented correctly](https://brandon3d.com/blender-face-orientation/), otherwise they might have weird collision. 
    
    The collision works depending on the normal direction, for example, if plane is facing to the top and the orientation also facing top, player can stand on the top of the plane, but they can pass through the bottom, but if the plane is facing to the top and the orientation is facing down, player will just pass through the plane, but they can't goes upward from bottom of the plane.