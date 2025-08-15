---
title: Export Material
order: 11
---

!!! warning "Warning"
    It is recommended to collapse this panel when not used. This panel process all object material for each action you do on viewport, which may cause minor lag and/or cause error on some context based operator.

## Export Material
Export material based on the selected object(s).

Exporting material will export them into `.txt` files, which should be placed at `resource/material/...`, and have exact filename as its mesh. Selecting multiple object assumes that you're trying to export [material that contain submesh](../MSH%20Panel/export_mesh.md).

## Entries
Contains material entry depending on the selected object(s). Ordered alphabetically.

Certain values are obtained either from the material themselves, or the custom properties. Some are editable, some are not.