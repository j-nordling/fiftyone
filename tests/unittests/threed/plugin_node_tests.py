"""
PluginNode unit tests.

| Copyright 2017-2026, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import json
import os
import tempfile
import unittest

from fiftyone.core.threed.object_3d import Object3D
from fiftyone.core.threed.plugin_node import PluginNode
from fiftyone.core.threed.scene_3d import Scene


def _base_node_dict(**overrides):
    """Build a minimal valid fo3d node dict for `_from_dict`."""
    d = {
        "_type": "Object3D",
        "name": "node",
        "visible": True,
        "position": [0, 0, 0],
        "quaternion": [0, 0, 0, 1],
        "scale": [1, 1, 1],
        "children": [],
    }
    d.update(overrides)
    return d


class TestPluginNodeConstruction(unittest.TestCase):
    def test_requires_plugin_type(self):
        with self.assertRaises(ValueError):
            PluginNode(name="x", plugin_type="")

    def test_default_data(self):
        node = PluginNode(name="x", plugin_type="custom")
        self.assertEqual(node.data, {})

    def test_to_dict_extra_shape(self):
        node = PluginNode(
            name="x",
            plugin_type="customNode",
            data={"fieldA": "abc"},
        )
        extra = node._to_dict_extra()
        self.assertEqual(
            extra,
            {"pluginType": "customNode", "data": {"fieldA": "abc"}},
        )


class TestPluginNodeRoundTrip(unittest.TestCase):
    def test_canonical_round_trip(self):
        scene = Scene()
        scene.add(
            PluginNode(
                name="asset-1",
                plugin_type="customNode",
                data={"fieldA": "abc-123", "fieldB": "vk1"},
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "scene.fo3d")
            scene.write(path)
            with open(path) as f:
                written = json.load(f)

        child = written["children"][0]
        self.assertEqual(child["_type"], "PluginNode")
        self.assertEqual(child["pluginType"], "customNode")
        self.assertEqual(
            child["data"], {"fieldA": "abc-123", "fieldB": "vk1"}
        )

    def test_data_keys_preserved_through_read(self):
        # The `data` dict's keys must appear on the read side exactly as
        # written, since the JS plugin component reads them verbatim.
        scene = Scene()
        scene.add(
            PluginNode(
                name="asset-1",
                plugin_type="customNode",
                data={"fieldA": "abc", "fieldB": "vk"},
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "scene.fo3d")
            scene.write(path)
            loaded = Scene.from_fo3d(path)

        loaded_child = loaded.children[0]
        self.assertIsInstance(loaded_child, PluginNode)
        self.assertEqual(loaded_child.plugin_type, "customNode")
        self.assertEqual(
            loaded_child.data, {"fieldA": "abc", "fieldB": "vk"}
        )

    def test_idempotent_re_emit(self):
        scene = Scene()
        scene.add(
            PluginNode(
                name="asset-1",
                plugin_type="customType",
                data={"someField": 42, "nested": {"innerField": "v"}},
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            p1 = os.path.join(tmp, "a.fo3d")
            p2 = os.path.join(tmp, "b.fo3d")
            scene.write(p1)
            Scene.from_fo3d(p1).write(p2)
            with open(p1) as f:
                d1 = json.load(f)
            with open(p2) as f:
                d2 = json.load(f)

        # `uuid` regenerates on construction unless preserved by `_from_dict`;
        # everything else should be identical.
        self.assertEqual(d1["children"][0]["pluginType"], "customType")
        self.assertEqual(d2["children"][0]["pluginType"], "customType")
        self.assertEqual(d1["children"][0]["data"], d2["children"][0]["data"])


class TestUnknownTypeRaises(unittest.TestCase):
    """
    `_from_dict` raises on any `_type` whose class isn't resolvable on
    `fiftyone.core.threed`. Plugin authors who want frontend-rendered
    custom nodes should use :class:`PluginNode`.
    """

    def test_unknown_type_raises(self):
        d = _base_node_dict(_type="UnregisteredCustom", field_a="abc")
        with self.assertRaisesRegex(ValueError, "Unknown fo3d node _type"):
            Object3D._from_dict(d)

    def test_known_type_does_not_raise(self):
        # Sanity: PluginNode itself still resolves and constructs.
        d = _base_node_dict(
            _type="PluginNode",
            plugin_type="customNode",
            data={"fieldA": "abc"},
        )
        node = Object3D._from_dict(d)
        self.assertIsInstance(node, PluginNode)


if __name__ == "__main__":
    unittest.main()
