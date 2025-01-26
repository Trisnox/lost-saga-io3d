import bpy
import itertools
import mathutils

from bpy.props import IntProperty, FloatVectorProperty, StringProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup

class FrameData(PropertyGroup):
    frame: IntProperty()
    location: FloatVectorProperty(size=3)
    rotation: FloatVectorProperty(size=4)

    def set(self, data):
        frame, location, rotation = data
        self.frame = frame
        self.location = location
        self.rotation = rotation

    def get(self):
        return (self.frame, mathutils.Vector(self.location), mathutils.Quaternion(self.rotation))


class BoneData(PropertyGroup):
    data: CollectionProperty(type=FrameData)
    bone_name: StringProperty()

    def __iter__(self):
        return (item.get() for item in self.data)

    def set(self, bone_name, data):
        self.bone_name = bone_name
        for frame_data in data:
            item = self.data.add()
            item.set(frame_data)

    def get(self):
        return [item.get() for item in self.data]


class AnimData(PropertyGroup):
    data: CollectionProperty(type=BoneData)
    name: StringProperty()
    frames: IntProperty()
    total_time: IntProperty()

    def __iter__(self):
        return ((item.bone_name, item) for item in self.data)

    def __getitem__(self, bone_name):
        anim = next((k for k in self.data if k.bone_name == bone_name), None)
        if anim is None:
            raise KeyError(f"Key '{bone_name}' not found")
        return anim

    def set(self, name, data):
        self.name = name
        for bone_name, frame_data in data.items():
            anim = self.data.add()
            anim.set(bone_name, frame_data)

    def get(self):
        return {
            anim.bone_name: anim.get()
            for anim in self.data
        }


class AnimationProperty(PropertyGroup):
    entry: CollectionProperty(type=AnimData)
    active_entry_index: IntProperty(default=0)

    def __getitem__(self, name):
        entry_data = next((nd for nd in self.entry if nd.name == name), None)
        if entry_data is None:
            raise KeyError(f"Animation '{name}' not found")
        return entry_data

    def remove(self, index):
        self.entry.remove(index)

    def set(self, anim_dict):
        while len(self.entry) > 0:
            self.entry.remove(0)

        name, data, _, frames, _, time = list(itertools.chain.from_iterable(anim_dict.items()))
        entry_data = self.entry.add()
        entry_data.set(name, data)
        entry_data.frames = frames
        entry_data.total_time = time

    def get(self):
        return {entry_data.name: entry_data.get() for entry_data in self.entry}

    def append(self, anim_dict):
        anim_data = self.get()

        name, data, _, frames, _, time = list(itertools.chain.from_iterable(anim_dict.items()))
        if name in anim_data:
            entry_data = next(nd for nd in self.entry if nd.name == name)
            for key_name, frame_data in data.items():
                bone_name = next((k for k in entry_data.data if k.name == key_name), None)
                if bone_name:
                    for tuple_data in frame_data:
                        item = bone_name.tuples.add()
                        item.set(tuple_data)
                else:
                    entry_data = entry_data.data.add()
                    entry_data.set(key_name, frame_data)
                    entry_data.frames = frames
                    entry_data.total_time = time
        else:
            entry_data = self.entry.add()
            entry_data.set(name, data)
            entry_data.frames = frames
            entry_data.total_time = time

    def append_entry(self, anim_name, bone_name, frame_data):
        entry_data = next((nd for nd in self.entry if nd.name == anim_name), None)
        if not entry_data:
            entry_data = self.entry.add()
            entry_data.name = anim_name

        bone_data = next((k for k in entry_data.data if k.name == bone_name), None)
        if not bone_data:
            bone_data = entry_data.data.add()
            bone_data.name = bone_name

        item = bone_data.tuples.add()
        item.set(frame_data)


def register():
    bpy.utils.register_class(FrameData)
    bpy.utils.register_class(BoneData)
    bpy.utils.register_class(AnimData)
    bpy.utils.register_class(AnimationProperty)
    bpy.types.Scene.io3d_animation_data = PointerProperty(type=AnimationProperty)


def unregister():
    del bpy.types.Scene.io3d_animation_data
    bpy.utils.unregister_class(AnimationProperty)
    bpy.utils.unregister_class(AnimData)
    bpy.utils.unregister_class(BoneData)
    bpy.utils.unregister_class(FrameData)