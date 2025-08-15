---
title: Resource Folder
order: 3
---

## Resource Folder
When set, imported mesh will always try to apply material if found. It will use material file located at `./material/...txt`, if none are found, then the mesh will not have any material.

You would only need to set the path on where the resource folder is, the resource folder structure should looked like this:
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