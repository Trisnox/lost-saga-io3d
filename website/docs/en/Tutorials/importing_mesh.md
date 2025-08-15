---
title: Importing Mesh
---

To import mesh, you can either go through `File > Import > Lost Saga Mesh (.msh)`, or through the n-panel, inside SKL/MSH panel, using the [`Import Mesh`](../SKL%20MSH%20Panel/mesh_import.md) button. After this, select the `.msh` files and import.

![type:video](../videos/mesh_import.mp4)

!!! tip "Textures"
    If you want the script to automatically assign texture, simply set the [`Resource Folder`](../SKL%20MSH%20Panel/resource_folder.md) path which leads to resource folder. The resource folder should have material and texture folder in order to import textures properly.

    This is the recommended way to set texture because the script automatically setup the texture and shading for you.

!!! info "Texture now showing"
    If you already set the resource folder, and the material is already applied but the texture is still not showing, the texture is already attached, your [viewport shading](https://docs.blender.org/manual/en/latest/editors/3dview/display/shading.html) just need to be changed. You can either set object color to texture, or change to material preview/rendered shading.

    ![I swear too many people asking this fucking issue](../images/texture_in_viewport.png)

!!! info "Object disappear on zoom out"
    If your object disappear when zooming out, this is because your [clip range is too small](https://docs.blender.org/manual/en/latest/troubleshooting/3d_view.html#troubleshooting-depth). Increase the clip end to see distant object, and increase the clip start to fix artifacts.

    ![type:video](../videos/clip_issue.mp4)