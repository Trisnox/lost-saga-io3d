import re
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class TextureUnit:
    """Represents a texture unit within a pass"""
    name: str = ""
    texture: str = ""
    tex_coord_set: int = 0
    colour_op: str = ""
    colour_op_ex: str = ""
    alpha_op: str = ""
    filtering: str = ""
    tex_address_mode: str = ""
    scale: List[float] = field(default_factory=list)
    scroll: List[float] = field(default_factory=list)
    rotate: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Pass:
    """Represents a pass within a technique"""
    name: str = ""
    ambient: List[float] = field(default_factory=list)
    diffuse: List[float] = field(default_factory=list)
    specular: List[float] = field(default_factory=list)
    emissive: List[float] = field(default_factory=list)
    shininess: float = 0.0
    vertex_program: str = ""
    fragment_program: str = ""
    vertex_program_ref: str = ""
    fragment_program_ref: str = ""
    cull_hardware: str = ""
    cull_software: str = ""
    lighting: bool = True
    depth_check: bool = True
    depth_write: bool = True
    depth_func: str = ""
    alpha_rejection: str = ""
    scene_blend: str = ""
    texture_units: List[TextureUnit] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Technique:
    """Represents a technique within a material"""
    name: str = ""
    scheme: str = ""
    lod_index: int = 0
    passes: List[Pass] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Material:
    """Represents a complete material definition"""
    name: str = ""
    parent: str = ""
    techniques: List[Technique] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


class Ogre3DMaterialParser:
    """Parser for Ogre3D material files"""

    def __init__(self):
        self.materials: List[Material] = []
        self.current_line = 0
        self.lines: List[str] = []

    def parse_file(self, file_path: str) -> List[Material]:
        """Parse an Ogre3D material file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> List[Material]:
        """Parse Ogre3D material content from string"""
        self.materials = []
        self.lines = [line.strip() for line in content.split('\n')]
        self.current_line = 0

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if not line or line.startswith('//'):
                self.current_line += 1
                continue

            if line.startswith('material'):
                self._parse_material()
            else:
                self.current_line += 1

        return self.materials

    def _parse_material(self):
        """Parse a material block"""
        line = self.lines[self.current_line]

        if not line.startswith('material'):
            self.current_line += 1
            return

        material = Material()
        material.name = 'material'

        self.current_line += 1
        self._expect_open_brace()

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if line == '}':
                self.current_line += 1
                break
            elif not line or line.startswith('//'):
                self.current_line += 1
                continue
            elif line.startswith('technique'):
                technique = self._parse_technique()
                material.techniques.append(technique)
            else:
                self._parse_property_line(line, material.properties)
                self.current_line += 1

        self.materials.append(material)

    def _parse_technique(self) -> Technique:
        """Parse a technique block"""
        line = self.lines[self.current_line]

        technique = Technique()

        match = re.match(r'technique\s*([^\s{]*)', line)
        if match and match.group(1):
            technique.name = match.group(1)

        self.current_line += 1
        self._expect_open_brace()

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if line == '}':
                self.current_line += 1
                break
            elif not line or line.startswith('//'):
                self.current_line += 1
                continue
            elif line.startswith('pass'):
                pass_obj = self._parse_pass()
                technique.passes.append(pass_obj)
            else:
                if line.startswith('scheme'):
                    technique.scheme = line.split(' ', 1)[1]
                elif line.startswith('lod_index'):
                    technique.lod_index = int(line.split(' ', 1)[1])
                else:
                    self._parse_property_line(line, technique.properties)
                self.current_line += 1

        return technique

    def _parse_pass(self) -> Pass:
        """Parse a pass block"""
        line = self.lines[self.current_line]

        pass_obj = Pass()

        match = re.match(r'pass\s*([^\s{]*)', line)
        if match and match.group(1):
            pass_obj.name = match.group(1)

        self.current_line += 1
        self._expect_open_brace()

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if line == '}':
                self.current_line += 1
                break
            elif not line or line.startswith('//'):
                self.current_line += 1
                continue
            elif line.startswith('texture_unit'):
                texture_unit = self._parse_texture_unit()
                pass_obj.texture_units.append(texture_unit)
            else:
                self._parse_pass_property(line, pass_obj)
                self.current_line += 1

        return pass_obj

    def _parse_texture_unit(self) -> TextureUnit:
        """Parse a texture_unit block"""
        line = self.lines[self.current_line]

        texture_unit = TextureUnit()

        match = re.match(r'texture_unit\s*([^\s{]*)', line)
        if match and match.group(1):
            texture_unit.name = match.group(1)

        self.current_line += 1
        self._expect_open_brace()

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if line == '}':
                self.current_line += 1
                break
            elif not line or line.startswith('//'):
                self.current_line += 1
                continue
            else:
                self._parse_texture_unit_property(line, texture_unit)
                self.current_line += 1

        return texture_unit

    def _parse_pass_property(self, line: str, pass_obj: Pass):
        """Parse pass-specific properties"""
        parts = line.split()
        if not parts:
            return

        prop = parts[0]

        if prop == 'ambient':
            pass_obj.ambient = self._parse_color(parts[1:])
        elif prop == 'diffuse':
            pass_obj.diffuse = self._parse_color(parts[1:])
        elif prop == 'specular':
            pass_obj.specular = self._parse_color(parts[1:])
        elif prop == 'emissive':
            pass_obj.emissive = self._parse_color(parts[1:])
        elif prop == 'shininess':
            pass_obj.shininess = float(parts[1])
        elif prop == 'vertex_program':
            pass_obj.vertex_program = parts[1]
        elif prop == 'fragment_program':
            pass_obj.fragment_program = parts[1]
        elif prop == 'vertex_program_ref':
            pass_obj.vertex_program_ref = parts[1]
        elif prop == 'fragment_program_ref':
            pass_obj.fragment_program_ref = parts[1]
        elif prop == 'cull_hardware':
            pass_obj.cull_hardware = parts[1]
        elif prop == 'cull_software':
            pass_obj.cull_software = parts[1]
        elif prop == 'lighting':
            pass_obj.lighting = parts[1].lower() in ('on', 'true', '1')
        elif prop == 'depth_check':
            pass_obj.depth_check = parts[1].lower() in ('on', 'true', '1')
        elif prop == 'depth_write':
            pass_obj.depth_write = parts[1].lower() in ('on', 'true', '1')
        elif prop == 'depth_func':
            pass_obj.depth_func = parts[1]
        elif prop == 'alpha_rejection':
            pass_obj.alpha_rejection = ' '.join(parts[1:])
        elif prop == 'scene_blend':
            pass_obj.scene_blend = ' '.join(parts[1:])
        else:
            self._parse_property_line(line, pass_obj.properties)

    def _parse_texture_unit_property(self, line: str, texture_unit: TextureUnit):
        """Parse texture unit specific properties"""
        parts = line.split()
        if not parts:
            return

        prop = parts[0]

        if prop == 'texture':
            texture_unit.texture = parts[1]
        elif prop == 'tex_coord_set':
            texture_unit.tex_coord_set = int(parts[1])
        elif prop == 'colour_op':
            texture_unit.colour_op = parts[1]
        elif prop == 'colour_op_ex':
            texture_unit.colour_op_ex = ' '.join(parts[1:])
        elif prop == 'alpha_op':
            texture_unit.alpha_op = parts[1]
        elif prop == 'filtering':
            texture_unit.filtering = ' '.join(parts[1:])
        elif prop == 'tex_address_mode':
            texture_unit.tex_address_mode = parts[1]
        elif prop == 'scale':
            texture_unit.scale = [float(x) for x in parts[1:]]
        elif prop == 'scroll':
            texture_unit.scroll = [float(x) for x in parts[1:]]
        elif prop == 'rotate':
            texture_unit.rotate = float(parts[1])
        else:
            self._parse_property_line(line, texture_unit.properties)

    def _parse_color(self, parts: List[str]) -> List[float]:
        """Parse color values"""
        try:
            return [float(x) for x in parts]
        except ValueError:
            return []

    def _parse_property_line(self, line: str, properties: Dict[str, Any]):
        """Parse a generic property line"""
        parts = line.split(None, 1)
        if len(parts) >= 2:
            key = parts[0]
            value = parts[1]

            parsed_value = self._parse_value(value)

            if key in properties:
                if isinstance(properties[key], list):
                    properties[key].append(parsed_value)
                else:
                    properties[key] = [properties[key], parsed_value]
            else:
                properties[key] = parsed_value

    def _parse_value(self, value: str) -> Any:
        """Parse a value string into appropriate type"""
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            try:
                numbers = [float(x) for x in value.split()]
                if len(numbers) == 1:
                    return numbers[0]
                else:
                    return numbers
            except ValueError:
                return value

    def _expect_open_brace(self):
        """Expect and consume an opening brace"""
        if self.current_line < len(self.lines) and self.lines[self.current_line] == '{':
            self.current_line += 1
        else:
            if self.current_line > 0:
                prev_line = self.lines[self.current_line - 1]
                if prev_line.endswith('{'):
                    return
                
            while self.current_line < len(self.lines):
                line = self.lines[self.current_line]
                if line == '{':
                    self.current_line += 1
                    break
                elif line.strip():
                    break
                self.current_line += 1

    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert parsed materials to dictionary format"""
        result = []
        for material in self.materials:
            material_dict = {
                'name': material.name,
                'parent': material.parent,
                'properties': material.properties,
                'techniques': []
            }

            for technique in material.techniques:
                technique_dict = {
                    'name': technique.name,
                    'scheme': technique.scheme,
                    'lod_index': technique.lod_index,
                    'properties': technique.properties,
                    'passes': []
                }

                for pass_obj in technique.passes:
                    pass_dict = {
                        'name': pass_obj.name,
                        'ambient': pass_obj.ambient,
                        'diffuse': pass_obj.diffuse,
                        'specular': pass_obj.specular,
                        'emissive': pass_obj.emissive,
                        'shininess': pass_obj.shininess,
                        'vertex_program': pass_obj.vertex_program,
                        'fragment_program': pass_obj.fragment_program,
                        'vertex_program_ref': pass_obj.vertex_program_ref,
                        'fragment_program_ref': pass_obj.fragment_program_ref,
                        'cull_hardware': pass_obj.cull_hardware,
                        'cull_software': pass_obj.cull_software,
                        'lighting': pass_obj.lighting,
                        'depth_check': pass_obj.depth_check,
                        'depth_write': pass_obj.depth_write,
                        'depth_func': pass_obj.depth_func,
                        'alpha_rejection': pass_obj.alpha_rejection,
                        'scene_blend': pass_obj.scene_blend,
                        'properties': pass_obj.properties,
                        'texture_units': []
                    }

                    for texture_unit in pass_obj.texture_units:
                        texture_unit_dict = {
                            'name': texture_unit.name,
                            'texture': texture_unit.texture,
                            'tex_coord_set': texture_unit.tex_coord_set,
                            'colour_op': texture_unit.colour_op,
                            'colour_op_ex': texture_unit.colour_op_ex,
                            'alpha_op': texture_unit.alpha_op,
                            'filtering': texture_unit.filtering,
                            'tex_address_mode': texture_unit.tex_address_mode,
                            'scale': texture_unit.scale,
                            'scroll': texture_unit.scroll,
                            'rotate': texture_unit.rotate,
                            'properties': texture_unit.properties
                        }
                        pass_dict['texture_units'].append(texture_unit_dict)

                    technique_dict['passes'].append(pass_dict)

                material_dict['techniques'].append(technique_dict)

            result.append(material_dict)

        return result
