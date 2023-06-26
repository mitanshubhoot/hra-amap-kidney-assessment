import numpy as np

def normalize(pcd):
    return pcd.scale(1 / np.max(pcd.get_max_bound() - pcd.get_min_bound()), center=pcd.get_center())

def denormalize(pcd, ref):
    return pcd.scale(np.max(ref.get_max_bound() - ref.get_min_bound()), center=ref.get_center())

def mean_bcpd(pointcloud):
    array = np.asarray(pointcloud.points).copy()
    mean = np.mean(array, axis=0)
    return mean

def scale_bcpd(pointcloud, mean):
    array = np.asarray(pointcloud.points).copy()
    scale = np.sqrt(np.sum(np.square(array - mean)) / (array.shape[0] * array.shape[1]))
    return scale

def normalize_bcpd(pointcloud, mean=None, scale=None):
    array = np.asarray(pointcloud.points).copy()
    # calculate mean
    if not isinstance(mean, np.ndarray):
        mean = mean_bcpd(pointcloud)

    # calculate scale
    if not isinstance(scale, float):
        scale = scale_bcpd(pointcloud, mean)

    # normalize and return
    array -= mean
    array /= scale
    return array

def denormalize_bcpd(pointcloud, mean=None, scale=None):
    array = np.asarray(pointcloud.points)
    # calculate mean
    if not isinstance(mean, np.ndarray):
        mean = mean_bcpd(pointcloud)

    # calculate scale
    if not isinstance(scale, float):
        scale = scale_bcpd(pointcloud, mean)

    # de-normalize and return
    array *= scale
    array += mean
    return array