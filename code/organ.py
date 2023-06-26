import yaml
import trimesh
import numpy as np

from pathlib import Path
from utils.io import load, make_export_dirs
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

    def export_projections(self, export_dir: str):
        # check if projections have been computed
        assert hasattr(self, 'registered'), "No projections found. Please run the registration pipeline first"

        # create appropriate export dirs
        parent_dir = make_export_dirs(export_dir)

        # save registered mesh
        self.registered.export(parent_dir / 'mesh' / 'registered.glb')

        # save rigid projection
        np.save(parent_dir / 'projections' / 'rigid_projection.npy', self.refine_registration)

        # save nonrigid projections
        np.save(parent_dir / 'projections' / 'dvf.npy', self.dvf)
        np.save(parent_dir / 'projections' / 'nonrigid_translation.npy', self.translation_nonrigid)
        np.save(parent_dir / 'projections' / 'nonrigid_scale.npy', self.scale_nonrigid)
        np.save(parent_dir / 'projections' / 'nonrigid_rotation.npy', self.rotation_nonrigid)

        # save correspondence
        self.correspondence.to_csv(parent_dir / 'correspondence' / 'correspondence.csv')

        # save the registration params
        with open(parent_dir / 'params.yaml', 'w') as file:
            yaml.dump(self.registered.params, file)
    
    def project(blocks: list):
        raise NotImplementedError
        
    

    


        