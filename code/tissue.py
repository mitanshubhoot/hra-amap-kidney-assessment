import trimesh
import numpy as np

from enum import Enum
from scipy.spatial.transform import Rotation

from utils.io import read_yaml


class DivisionFactor(Enum):
    millimeter = 1e3
    centimeter = 1e2
    meter = 1

class TissueBlock(trimesh.Trimesh):
    def __init__(self, sample: dict, metadata: dict = None) -> None:
        super(TissueBlock, self).__init__()
        self.mappings = read_yaml('../atlas_paths.yaml')
        self.id = sample['@id']
        self.donor_id = self.id.split('_')[0]
        self.target = trimesh.load(self.mappings['RUI'][sample['rui_location']['placement']['target'].split('#')[-1]], 
                                   force='mesh')
        self.dimension_units = sample['rui_location']['dimension_units']
        self.size, self.scaling, self.translation, self.rotation = self._unpack_spatial_params(sample)
        self.faces, self.vertices = self._build()

    def _unpack_spatial_params(self, sample):
        division_factor = getattr(DivisionFactor, self.dimension_units).value

        # size
        size = (sample['rui_location']['x_dimension'] / division_factor, 
                sample['rui_location']['y_dimension'] / division_factor, 
                sample['rui_location']['z_dimension'] / division_factor)
        
        # scale
        scaling = (sample['rui_location']['placement']['x_scaling'], 
                   sample['rui_location']['placement']['y_scaling'], 
                   sample['rui_location']['placement']['z_scaling'])
        
        # translation
        translation = (sample['rui_location']['placement']['x_translation'] / division_factor, 
                        sample['rui_location']['placement']['y_translation'] / division_factor, 
                        sample['rui_location']['placement']['z_translation'] / division_factor)

        # rotation
        rotation = (sample['rui_location']['placement']['x_rotation'], 
                    sample['rui_location']['placement']['y_rotation'], 
                    sample['rui_location']['placement']['z_rotation'])     
        
        return (size, scaling, translation, rotation)  
    
    def _locate_origin(self):
        """Calculate the bottom-back-left corner of the target organ"""
        bbox_coords = self.target.bounding_box_oriented.vertices
        bottom_left_corner = bbox_coords[bbox_coords.sum(axis=1).argmin()]
        return bottom_left_corner
    
    def _place_on_target(self, box):
        """Apply necessary transforms to place the box where it is registered"""
        # apply scaling
        box = box.apply_scale(self.scaling)

        # find rotation matrix from angles
        rotation_matrix = Rotation.from_euler(seq='xyz', angles=self.rotation, degrees=True).as_matrix()
        # convert to 4x4 transformation matrix
        rotation_transform = np.empty((4, 4))
        rotation_transform[:3, :3] = rotation_matrix
        rotation_transform[:3, 3] = [0, 0, 0]
        rotation_transform[3, :] = [0, 0, 0, 1]
        # apply rotation
        box = box.apply_transform(rotation_transform)
    
        # apply translation
        box = box.apply_translation(self.translation)

        return box
    
    def _build(self):
        # create box mesh
        box = trimesh.creation.box(extents=self.size)

        # find origin of the target organ
        origin = self._locate_origin()
    
        # place origin of the box at the bottom-back-left
        box = box.apply_translation(origin)
        
        # move box according to transforms
        box = self._place_on_target(box)
        
        # return
        return (box.faces, box.vertices) 
    
    def show_on_target(self):
        return trimesh.scene.Scene(geometry=[self, self.target]).show()