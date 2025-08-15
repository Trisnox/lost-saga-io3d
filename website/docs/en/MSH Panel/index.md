---
title: MSH and Material Info Panel
---
# Overview

![msh panel](../images/msh_panel.png)
![material info panel](../images/material_info_panel.png)

## Mesh Utility:
- Export Collision: Export selected mesh as collision mesh (`.cms`)
- Export Mesh: Export active/selected mesh file(s) as `.msh`. If more than one mesh is selected, then the mesh will have submeshes, it is ordered alphabetically
- Surpress Split: When enabled, `Preview Split` will not split the mesh. Assumes manual split
- Preview Split: Duplicate the object, then split the mesh (or not depending surpress split), and then change the UV map as if they were being displayed in-game
- Split Mesh: Split the mesh based off threshold. They will be separated based on indices
- Maximum Faces: Used for split mesh, each separated mesh will not have more than this specified faces
- Get Bounding: Get bounding box and its sphere radius, and then copy them to clipboard (copy only works for windows). You would need this for `.txt` files located at `resource/model/`

## Material Utility
- Import Losa Shader: Import all node groups from `losa shader.blend` located at root folder of the script
- Generate Material: Generate material for active object. One of the four options can be choosed
- Turn Material into Opaque: Set the material into opaque
- Turn Material into Transparent: Set the material into transparent
- Toggle Shadeless: toggle shaded/shadeless

## Visibility
- Toggle Backface Culling: Toggle backface culling for all material except outline material (which should always active)
- Toggle Outline: Toggle all outline that uses solidify modifier/inverse hull method

## Material Info
It is recommended to collapse this panel when not used.

- Export Material: Export material based on the selected object(s)
- Entry: Contains material entry depending on the selected object(s). Ordered alphabetically