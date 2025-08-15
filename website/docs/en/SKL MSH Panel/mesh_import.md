---
title: Mesh Import
order: 2
---

## Import
You can import mesh files (`.msh`) through io3d n-panel, inside `SKL/MSH` panel > Import Mesh, or through `File > Import > Lost Saga Mesh (.msh)`.

![msh_import_operator.png](../images/msh_skin_tones.png)

!!! tip "Multi-file support"
    This operator support processing multiple files at once. Simply select all files you want to import, and then the script will import all of them individually.

## Default Skin Color
Only works if resource folder is set, ignored if not specified.

If the mesh contain a skin, it will use this choice of skin tone. Do note that their shading might not looked exactly the same when compared in-game.

## Merge Faces
When enabled, the imported mesh will have their vertices merged on points where they're overlaping each other. If you're using `Generate Outline` option, this will help make the solidify modifier become cleaner. Please view [in-depth explanation about split mesh](../MSH%20Panel/preview_split.md) for more info.

## Generate Outline
When enabled, the imported mesh will be accompanied by outlines based off the material outline color if provided. By default, the generated outline will use [inverse hull method](https://bnpr.gitbook.io/bnpr/outline/inverse-hull-method).

## Use Rim Light Instead
When enabled, generated outline will use rim light instead of inverse hull method.

## Surpress Color
When enabled, outline will not use the color provided by the material file if provided. Instead, the mesh will use black color, which is shared across all other mesh that have outline

## Separate Material
When enabled, each mesh will have different outline material instead of using the shared one