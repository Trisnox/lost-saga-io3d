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