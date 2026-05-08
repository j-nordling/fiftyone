"""
Generic carrier for fo3d nodes rendered by a frontend plugin.

| Copyright 2017-2026, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

from typing import Optional

from .object_3d import Object3D
from .transformation import Quaternion, Vec3UnionType


class PluginNode(Object3D):
    """A fo3d scene node whose rendering is provided by a frontend plugin.

    Plugin authors who want to author fo3d scenes from Python without
    defining a custom :class:`Object3D` subclass can construct a
    ``PluginNode`` directly. The ``plugin_type`` string is matched
    (case-insensitively) against the ``typeName`` passed to
    ``registerNodeType`` in the plugin's JS bundle. The ``data`` dict is
    passed through opaquely to the plugin component as the ``data`` prop;
    its keys appear on the JS side exactly as you wrote them in Python.

    Example::

        scene.add(fo.PluginNode(
            name="asset-1",
            plugin_type="customNode",
            data={"fieldA": "abc-123", "fieldB": "value"},
        ))

    Args:
        name (str): the name of the node (must be unique within the scene)
        plugin_type (str): the registered node type the frontend plugin
            uses to identify this node; matched case-insensitively
        data (None): a JSON-serializable dict forwarded to the plugin
            component as its ``data`` prop
        visible (True): default visibility of the node in the scene
        position (None): the position of the node in object space
        quaternion (None): the quaternion of the node in object space
        scale (None): the scale of the node in object space
    """

    def __init__(
        self,
        name: str,
        plugin_type: str,
        data: Optional[dict] = None,
        visible: bool = True,
        position: Optional[Vec3UnionType] = None,
        scale: Optional[Vec3UnionType] = None,
        quaternion: Optional[Quaternion] = None,
    ):
        super().__init__(
            name=name,
            visible=visible,
            position=position,
            scale=scale,
            quaternion=quaternion,
        )
        if not plugin_type:
            raise ValueError("PluginNode requires a non-empty plugin_type")
        self.plugin_type = plugin_type
        self.data = data or {}

    def _to_dict_extra(self):
        return {"pluginType": self.plugin_type, "data": self.data}
