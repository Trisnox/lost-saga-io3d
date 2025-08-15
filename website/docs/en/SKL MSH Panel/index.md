---
title: SKL MSH Panel
---
# Overview

![SKL/MSH Panel](../images/skl_msh_panel.png)

- Import Skeleton: Import skeleton files `.skl`
- Import Mesh: Import mesh files `.msh`
- Import Collision: Import mesh collision files `.cms`

## Resource Folder

- Resource Folder: When set, import mesh will always try to apply material if found. The resource folder structure should looked like this:
```bash
└─resource
  ├─animation
  │  └─trail_ani
  ├─effect
  ├─font
  ├─material
  ├─mesh
  ├─model
  │  ├─animodel
  │  └─staticmodel
  ├─skeleton
  ├─tables
  ├─text
  ├─texture
  │  ├─decalbase
  │  └─effecttexture
  └─wave
      └─bgm
```

## Utility

- Attach Armature: One click solution to add armature modifier to all mesh, and using the selected armature as the target
- Rename Bones: Rename Lost Saga Bones to Blender and vice versa
- Setup Scene: One click solution to setup scene to match Lost Saga scene setting