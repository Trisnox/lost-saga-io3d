---
title: Generate Material
order: 7
---

## Generate Material
An operator to generate material, can choose one out of four options. Intended for creating mesh from scratch.

This operator will automatically import the nodes, there is no need to import the nodes beforehand. This operator will automatically set the `shader_type` property inside material `Custom Properties`. Aside from those, this operator will automatically setup the nodes for you, depending on which type you choose, so you would only need to set the texture and setting the outline color (can remove the rgb and value nodes if you do not want outline). Make sure to have blank material slot, otherwise this script will error.

This is intended to be used with [`Export Material` operator](../MSH%20Panel/export_material.md).

[Please refer to `Export Mesh` operator to see what each options are for](../MSH%20Panel/export_mesh.md). Choosing `Skin` will counts as `Animation`.

![material types](../images/material_types.png)

!!! bug "Known issue"
    [`Generate Material operator, Line 83-89`](https://github.com/Trisnox/lost-saga-io3d/blob/main/operators/generate_material.py#L83-L91), will attempt to switch area context to shader editor, ungroup the node group, and then finding respective node after ungrouping. However, this will cause error if the first slot of material was not the material generated from this operator. Unfortunately, the [Blender API does not have the ungroup function without using `bpy.ops`](https://docs.blender.org/api/current/search.html?q=ungroup&check_keywords=yes&area=default) (which usually limited to certain context area). This issue is considered as 'cannot fix'.