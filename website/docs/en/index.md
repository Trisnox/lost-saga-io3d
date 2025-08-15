# Lost Saga IO3D
Blender add-on to import/export various Lost Saga formats. Supported files are `skl`/`msh`/`cms`/`ani`

Main repository [github.com/Trisnox/lost-saga-io3d](https://github.com/Trisnox/lost-saga-io3d)

<div class="grid cards" markdown>

-   :fontawesome-solid-download:{ .lg .middle } __Installation__

    ---

    Guide on how to install the add-on

    [:octicons-arrow-right-24: Installation](./install.md)

-   :material-book-open-variant:{ .lg .middle } __Tutorial/Guide__

    ---

    Guide on how to operate the add-on

    [:octicons-arrow-right-24: Tutorial/Guides](./Tutorials/index.md)
    
</div>

___
Or if you're looking for an in-depth explanation about certain operator/button

<div class="grid cards" markdown>

-   :material-human::material-cube-outline:{ .lg .middle } __SKL/MSH Panel__

    ---

    **SKL/MSH Panel**<br>
    Panel to import skeleton, mesh/collision, or general utility

    [:octicons-arrow-right-24: SKL/MSH Panel](./SKL%20MSH%20Panel/index.md)

-   :material-cube-outline:{ .lg .middle } __MSH Panel__

    ---

    **MSH Panel**<br>
    Panel to operate with meshes, such as exporting mesh/collision, or change shader

    [:octicons-arrow-right-24: MSH Panel](./MSH%20Panel/index.md)

-   :material-walk:{ .lg .middle } __ANI Panel__

    ---

    **ANI Panel**<br>
    Panel to operate with animation, such as importing/exporting animation, skeleton operations, and applying animations

    [:octicons-arrow-right-24: ANI Panel](./ANI%20Panel/index.md)
    
</div>

___
Or other topics

<div class="grid cards" markdown>

-   :octicons-file-binary-16:{ .lg .middle } __Binary Structure__

    ---

    **Binary Structure**<br>
    Post explaining about the binary structure of losa 3d formats

    [:octicons-arrow-right-24: Binary Structure](./binary_structure.md)

-   :octicons-file-16:{ .lg .middle } __Sample Files__

    ---

    **Sample Files**<br>
    Project files as well their resource pack made with the add-on

    [:octicons-arrow-right-24: Sample Files](./sample_files.md)

-   :material-calendar-text:{ .lg .middle } __Events Editor__

    ---

    **Events Editor**<br>
    Simple script to edit events on `.ani` files

    [:octicons-arrow-right-24: Events Editor](./events_editor.md)
    
</div>

## Features
- Import/Export various formats, such as: skeleton (`.skl`), mesh (`.msh`), mesh collision (`.cms`), animation (`.ani`). Result is almost similar when compared in-game and vice versa
- Blender skeleton integration, such as: rename losa bones to blender and vice versa, various skeleton import mode (lite, advanced, retarget), operator to help with animating, and many more
- Many operators to operate with meshes as well the ability to export them, such as: export material, calculate bounding box, preview mesh split, split mesh based off threshold, shader to imitate Lost Saga (toon shader and various skin tones), and many more
- Animation entries table. This table can be used to re-use animation that has been previously imported without the need to re-import the animation again, this table also automatically calculate keyframe count based on scene fps

## Note
Lost Saga measure their unit in meters, while blender measure them in centimeters, this will cause any objects imported to appear 10x larger in Blender. [Setup Scene Operator](./SKL%20MSH%20Panel/setup_scene.md) was made to fix this issue in one click

Also worth noting that Lost Saga derives their coordinate [system from DirectX](binary_structure.md), but this script already handle such difference for both import/export

Lost Saga might also uses modified Ogre3D as their renderer

## Special Thanks
Thanks to zex (imageliner on Discord) for showing me the correct rotation for Lost Saga skeleton

## To-Do
!!! info "to-do"
    === "Rewrite Retarget"
        The current script is just basically proof of concept, it is possible to retarget animation into Lost Saga skeleton, exporting the animation, and then apply it back to Lost Saga skeleton in order to be exported.
        
        However, the current solution, which is creating advanced skeleton, but with `origin_correction` set without rotation/scale, and then apply the transformation of all bones, which was hoped so that it preserve the bone direction and coordinate system, somewhat succeed, but the final result is nowhere close (likely because the the source armature had to be modifed to match the target armature). 
        
        However, I recently discovered about delta transformation, and I might be able to make use of this.
    
    === "Events"
        What I had in mind was creating a text/enum property, which can be accessed through panel. And guess what? We can insert keyframes to properties as well. This make events doable. With enum, I can try to list all possible events (including custom user defined as well), and then the user just simply need to insert keyframe. The script will then read the animation data, which then the animation can export alongside the events. It might only insert event if it comes in pairs in same frame, otherwise they won't append event.

        Unfortunately, there is no way to force pair an insert keyframe (as far as I know).
        
        ![ui mockup](./images/event_mockup.png)

## Support
You can contact me through Discord ([trisnox](https://discord.com/users/543595002031243300)) or through my [Discord server](https://discord.gg/dJUMU9Gkw2)