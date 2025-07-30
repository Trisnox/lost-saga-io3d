SKIN_COLOR_DICT = {  # Light, Skin Shadow, Shadow
    'VANILLA': ((1.0, 0.982, 0.591, 1.0), (0.557, 0.005, 0.002, 1.0), (0.557, 0.211, 0.14, 1.0)),
    'PEACH': ((0.982, 0.680, 0.238, 1.0), (0.557, 0.005, 0.002, 1.0), (0.481, 0.27, 0.145, 1.0)),
    'APRICOT': ((0.991, 0.418, 0.107, 1.0), (0.557, 0.005, 0.002, 1.0), (0.317, 0.159, 0.109, 1.0)),
    'CHOCOLATE': ((0.216, 0.051, 0.01, 1.0), (0.035, 0.000344, 0.000344, 1.0), (0.13, 0.024, 0.048, 1.0)),
    'PALE': ((0.474, 0.407, 0.533, 1.0), (0.211, 0.0, 0.0, 1.0), (0.107, 0.081, 0.251, 1.0)),
    'FROZEN': ((0.223, 0.930, 0.991, 1.0), (0.103, 0.0, 0.222, 1.0), (0.034, 0.353, 0.198, 1.0)),
    'GREEN': ((0.262, 0.270, 0.056, 1.0), (0.179, 0.0, 0.0, 1.0), (0.059, 0.136, 0.032, 1.0)),
    'UNDEAD': ((0.054, 0.03, 0.025, 1.0), (0.019, 0.002, 0.0, 1.0), (0.033, 0.012, 0.013, 1.0)),
    'GREY': ((0.8, 0.8, 0.8, 1.0), (0.083, 0.138, 0.288, 1.0), (0.285, 0.395, 0.509, 1.0))
}

TOON_SHADER_INDEX = {
    'color/texture': 0,
    'shadow color': 1,
    'threshold': 2,
    'diffuse blend': 3,
    'alpha': 4,
    'opacity': 5,
    'invert opacity': 6,
    'is transparent': 7,
    'emission color': 8,
    'emission strength': 9,
    'preserve color': 10,
    'specular color': 11,
    'specular strength': 12,
    'specular roughness': 13,
    'ambient color': 14,
    'ambient strength': 15,
    'rim light color': 16,
    'rim light strength': 17,
    'rim light thickness': 18,
    'rim light ior': 19
}

class MeshData:
    def __init__(self, *args):
        self.min_index = args[0]
        self.vertex_count = args[1]
        self.index_start = args[2]
        self.face_count = args[3]
    
    def __iter__(self):
        yield self.min_index
        yield self.vertex_count
        yield self.index_start
        yield self.face_count
    
class BlendWeight:
    def __init__(self, *args):
        self.weight = args[0]
        self.biped_id = args[1]

class MeshType:
    def __init__(self, *args):
        self.types = {
            0: 'STATIC',
            1: 'ANIMATION',
            2: 'LIGHTMAP',
            3: 'BILLBOARD',
            4: 'NORMAL_BILLBOARD',
            5: 'ANIMATE_EFFECT',
            6: 'STATIC_VERTEX_COLOR'
        }
        self.enum = int(args[0])
        self.type = self.types[self.enum]
    
    def __str__(self):
        return self.type