![blender_09-01-2025_17-16-58](https://github.com/user-attachments/assets/81e0ccc4-e4dc-43d4-9dad-47e8f554c572)

# Lost Saga IO3D
Blender add-on to import/export various Lost Saga formats. Supported files are `skl`/`msh`/`ani`.

# Installation
[Download this addon](https://github.com/Trisnox/lost-saga-io3d/releases/latest), then either drag and drop zip into blender, or go to `Edit > Preferences > Add-ons > Install from disk` and select the zip file.

# Usage
Skeleton and mesh can be imported through File > Import > Lost Saga Skeleton/Mesh (`.skl`/`.msh`).

Panel is also available on 3d view, labeled `IO3D` on sidebar.

# Features
- Skeleton import, as armature or empty
- Mesh import, including normals, UVmap, weights, and texture (doesn't support `IOFVF_POSITION2` or `point version` meshes)
- Resource Folder path. If set, mesh will automatically import texture if found one.
- Rename armature bones to Blender or Lost Saga and vice versa



https://github.com/user-attachments/assets/4989d79a-0754-40c3-8ca6-474f6e8f4927



# Experimental Features
## Animation
Animation can be imported, as well forming armature from it. Animation is currently imported as-is without handling the axis differences.

In order to import animation as well applying animation into meshes, import the skeleton as empty, form armature, attach armature with mesh, and then import the animation. This will ensure the mesh to properly transform.

## Mesh Export
Mesh can be exported, it also convert axis differences as well. Also, user doesn't need to triangulate model, rotate model, or flip UV maps before exporting, the script does that for convenience.

# Note
Lost Saga uses y-up axis left handed, while Blender uses z-up axis right handed. For armature, Lost Saga uses x-axis rotation for head to tail bone rotation, and Blender uses y-axis for head to tail bone rotation. These axis differences needs to be handled properly when trying to import to Blender.

Objects also appear 100x larger on Blender than on Lost Saga, this can be fixed easily by changing the unit scale into 0.01 on Blender, and increasing the Clip End on 3d view to prevent clipping.

# Special Thanks
![zex's pfp](https://cdn.discordapp.com/avatars/168260795233206272/a_0b2d1becd61b1f08965a0a4f87b96c69.gif?size=128)
Thanks to zex (imageliner on Discord) for showing me the correct rotation for Lost Saga skeleton.

# To-do
- Animation exporter
- Skeleton exporter
- IK for legs and hands
- Texture transparency. Certain texture models might require transparency, especially effects.
- Events handler (animation have events, which stores certain event such as audio, sfx, fx, and many more. The resource folder can be used for this)

# Support
You can contact me through discord ([trisnox](https://discord.com/users/543595002031243300)) or through my [discord server](https://discord.gg/dJUMU9Gkw2).
