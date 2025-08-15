---
title: Preview Split
order: 3
---

Not to be confused with [Split Mesh](../MSH%20Panel/split_mesh.md).

???+ question "Differences"

    `Split Mesh` operator is to separate mesh into chunks, meanwhile `Preview Split` operator is to split mesh in attempt to fix UV issues before exporting

## Preview Split
An operator to preview the UV as if they were displayed in-game. This will also automatically split edges on where vertices have two different coordinate on UV. The object will be duplicated, and the duped object will show their modified UV.

If `Surpress Split` is enabled, then the mesh will not be split. This assumes that you're manually split the mesh yourself.

This process is crucial, if you were to export the UV as is, it will become somewhat distorted. This is due to how Lost Saga store their UV map. Each vertices can only have one UV coordinate only, if they have more than one, then a face will be created with the latest indices instead. This process will also cause vertices amount to increase slightly.

![split distortion](../images/split_distortion.png)