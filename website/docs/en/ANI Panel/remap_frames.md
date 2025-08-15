---
title: Remap Frames
order: 5
---

## Remap Frames
Remap keyframes based off the old/new time stretching.

!!! warning "Warning"
    This operator is intended if you use `Output > Frame Range > Time Stretching` while having 100 fps, trying to use any other value might be inaccurate. It is expected that the frame map new is equivalent to project fps.
    
!!! note "Time Stretching"
    Using time stretching allows you to remap the keyframes into approtiate timings. For example, if you were to insert video into viewport, the video speed correlate with the project/scene FPS, so running a 30fps video on 100fps scene will cause it to play ~3x as fast. But with time stretching, you'll be able to animate on 30fps while using 100fps scene, after you're done animating, you then can use remap frames to automatically remap the frames based off the old/new FPS.

    To use this, simply set project FPS, let's just say 60fps, set the old time stretching to `30` or any other FPS you desire, and then set the new time stretching to `60` which match the project FPS.