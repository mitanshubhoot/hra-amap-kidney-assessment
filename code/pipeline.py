import yaml

from registration import rigid_registration, nonrigid_registration
from utils.preprocess import normalize
from utils.metrics import sinkhorn, chamfer, hausdorff
from utils.transforms import pointcloud_to_mesh
from organ import Organ


class RegistrationPipeline():
    def __init__(self, params: str) -> None:
        with open(params) as f:
            self.params = yaml.safe_load(f)

    def _hyperparamter_search():
        raise NotImplementedError
    
    def _autotune():
        raise NotImplementedError

    def run(self, source: Organ, target: Organ):
        # normalize
        source.pointcloud, target.pointcloud = normalize(source.pointcloud), normalize(target.pointcloud)

        # rigid registration
        source = rigid_registration(source, target, params=self.params['rigid_registration'])

        # nonrigid registration
        source = nonrigid_registration(source, target, params=self.params['nonrigid_registration'])

        # registered organ
        source.registered = pointcloud_to_mesh(source.transformed_nonrigid, source.faces)

        # add registration params to the registered organ
        source.registered.params = self.params

        return source
    
    def compute_metrics(self, metric: str):
        if metric not in ['sinkhorn, chamfer, hausdorff']:
            raise ValueError(f"{metric} not recognized, must be one of sinkhorn, chamfer or hausdorff")
        return metric(self.result)
    
