---
title: Split Mesh
order: 4
---

Not to be confused with [Preview Split](../MSH%20Panel/preview_split.md).

???+ question "Differences"

    `Preview Split` operator is to split mesh in attempt to fix UV issues before exporting, meanwhile `Split Mesh` operator is to separate mesh into chunks

## Split Mesh
Split active mesh object based off threshold set on `Maximum Faces`.

This operator will duplicate the active object, and then hide the original object.

This will split mesh into chunks based on the threshold set on `Maximum Faces`, each chunk cannot have more than specified amount. This is useful to avoid overflow error when trying to load mesh with too many polygons.

Lost Saga will fail to load mesh that hit certain limit, this limit only applies to each mesh, but the scene can have as many polygons without issues. The maximum limit is not tested, but it should be safe to have about 20k polygons. Also do note that even with submesh, Lost Saga sums the total amount of polygons regardless of submesh, as submesh only used to allow mesh to have different material.

This will also preserve UV map and normals.

![split mesh](../images/split_mesh.png)