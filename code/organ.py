import trimesh

from pathlib import Path
from utils.io import load
from utils.transforms import mesh_to_pointcloud

class Organ(trimesh.Trimesh):
    def __init__(self, path: str, metadata: dict = None) -> None:
        super(Organ, self).__init__()
        self.path = Path(path)
        self.file_name = self.path.stem
        self.file_type = self.path.suffix
        self.faces, self.vertices = load(self.path, self.file_type)
        self.pointcloud = mesh_to_pointcloud(self)
        if metadata:
            self.metadata = metadata
    
    def project(blocks: list):
        raise NotImplementedError
        
    

    


        