"""
3D Gaussian Splat definitions for FiftyOne.

| Copyright 2017-2026, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

from typing import Optional

from .object_3d import Object3D
from .transformation import Quaternion, Vec3UnionType


class GaussianSplat(Object3D):
    """Represents a 3D Gaussian Splat rendered from a PLY file via the
    ``@sparkjsdev/spark`` library.

    Args:
        name (str): the name of the splat
        ply_path (str): path to the PLY file containing the Gaussian splat data
        visible (True): default visibility of the splat in the scene
        position (None): the position of the splat in object space
        quaternion (None): the quaternion of the splat in object space
        scale (None): the scale of the splat in object space
    """

    def __init__(
        self,
        name: str,
        ply_path: str,
        visible: bool = True,
        position: Optional[Vec3UnionType] = None,
        scale: Optional[Vec3UnionType] = None,
        quaternion: Optional[Quaternion] = None,
    ):
        """Initializes a :class:`GaussianSplat`."""
        super().__init__(
            name=name,
            visible=visible,
            position=position,
            scale=scale,
            quaternion=quaternion,
        )

        if not ply_path:
            raise ValueError("GaussianSplat requires a ply_path")

        self.ply_path = ply_path

    def _to_dict_extra(self):
        return {"plyPath": self.ply_path}
