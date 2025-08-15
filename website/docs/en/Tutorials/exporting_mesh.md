---
title: Exporting Mesh
---

Exporting mesh is actually quite simple, you just need to select an object, and then use the [`Export Mesh`](../MSH%20Panel/export_mesh.md) operator, or through `File > Export > Lost Saga Mesh (.msh)`. The script will automatically triangulate, attempt fixing UV (if surpress split is disabled), and convert coordinate differences. If you select more than one mesh, then the mesh will contain submesh. This is useful if you want to have different material for each object. Also keep in mind that triangulate will double your face count if the mesh contain quads, this wouldn't be problem if your mesh only contain triangles. [This is by design for all game engine](https://gamedev.stackexchange.com/questions/9511/why-do-game-engines-convert-models-to-triangles-instead-of-using-quads).

!!! tip "Material"
    Mesh files does not contain any material data, they are instead separated inside `resource/material/.txt` file. Use the [`Export Material` operator inside Material Info entry panel](../MSH%20Panel/export_material.md#export-material) to export material of selected object(s).

!!! tip "Preview Split"
    It is important that you always check for the UV map before exporting by using the [`Preview Split` operator](../MSH%20Panel/preview_split.md). This operator will create a duplicate object that shows the UV map as if it was in-game. By default, it will always try to split the vertices where it will break the UV, but you can also manually split them by enabling `Surpress Split` if you want to.


## Submesh
To create submesh, in edit mode, you can simply select the faces you want to separate. After separation, you should name your mesh with `_1/_2/_3/...` suffix, as the mesh and material exporter is ordered alphabetically. If you have more than 10 meshes, just simply add `_01/_02/_03/...` suffix. But keep in mind that submesh does not bypass the mesh limit, use [`Split Mesh`](../MSH%20Panel/split_mesh.md) instead if you want more vertex/face on your mesh without causing the overflow error.

!!! warning "Warning"
    Keep in mind that if you use submesh, all mesh should have the same type of material type. Eg: the first part of mesh is generated using static, then the rest of the part should be static as well.
    
    A mesh cannot have different material type (except animation and skin, as they share the same vertex mask flag), this is because a single mesh file shares [vertex mask](../binary_structure.md#vertex-component) for a mesh and its submeshes, so having both or all static/lightmap/animation within single file is not possible.

## Static Mesh
Static Mesh is by far the easiest mesh to export, as they only contain normals, and single UV map.

If you use [`Generate Material`](../MSH%20Panel/generate_material.md) operator, it should be generated using `Static` option.

## Lightmap Mesh
Lightmap have slightly complex, as they have two textures, and two UV map, but they cannot have normals. The UV map doesn't explicitly need to be different as the first one though, it's valid as long it has two UV map regardless.

If you use [`Generate Material`](../MSH%20Panel/generate_material.md) operator, it should be generated using `LightMap` option, this will also create secondary UV map if you haven't.

!!! info "Collision Mesh"
    If you're exporting maps, you should also export the collision as well by using the [export collision operator](../MSH%20Panel/export_collision.md). The lazy way to export collision is to just reuse the mesh.

## Animation Mesh
Animation mesh is somewhat complex, the hard part is to weight painting the mesh, but otherwise they share similar trait to static, wherea animation contain normals, single UV map, and weights. First, [import skeleton](../SKL%20MSH%20Panel/skeleton_import.md) using lite mode. Attach the skeleton and armature, and you can optionally [rename bones](../SKL%20MSH%20Panel/rename_bones.md) if you want to use symmetrize function, which automatically copy your weight paint to opposite side as long the bone name can be recognized by Blender and the mesh is perfectly symmetrical (use [Topology Mirror](https://docs.blender.org/manual/en/latest/modeling/meshes/tools/tool_settings.html?#bpy-types-mesh-use-mirror-topology) if that doesn't work).

!!! info "Renaming bones"
    If you use rename bones operator, make sure to rename them again before exporting the mesh. This is because exported mesh will have their vertex group name exported. The script does not automate these name conversion yet.

If you use [`Generate Material`](../MSH%20Panel/generate_material.md) operator, it should be generated using `Animation` option, or `Skin` if you want that part of mesh to be a skin color.

![type:video](../videos/weight_painting.mp4)

!!! tip "Sample Files"
    Still confused? check the [sample files here](../sample_files.md).