---
title: Export Mesh
order: 2
---

## Export Mesh

![export mesh operator](../images/export_mesh_operator.png)

`Don't split faces` will surpress mesh split. You should preview the split first to check if the UV are correct, since UV will always somewhat broken if not properly split. Please view [in-depth explanation about split mesh](../MSH%20Panel/preview_split.md) for more info.

Exporting mesh will automatically convert the coordinate difference and triangulate the mesh(es), so there is no need to rotate or triangulate the mesh beforehand. Also keep in mind that triangulate will double your face count if the mesh contain quads, this wouldn't be problem if your mesh only contain triangles. [This is by design for all game engine](https://gamedev.stackexchange.com/questions/9511/why-do-game-engines-convert-models-to-triangles-instead-of-using-quads).

When choosing more than one mesh, then the mesh will have submesh, it is ordered alphabetically. For naming convention, you can add suffix like `_1/_2/_3` to each submesh. Submesh allows for each mesh to have different material.

When exporting mesh, you can choose one of the three types of the mesh

[Refer to vertex component on how the flag works](../binary_structure.md/#vertex-component)

- Static: For static mesh, usually background objects. Contains: position, normals, and UV
- Lightmap: For static mesh with two UV map, usually background objects. Contains: position, UV, and lightmap UV
- Animation: For mesh with weights, usually gear, player model, and more. Contains: position, normals, UV, and weights and indices

You can also choose not to export certain flags.