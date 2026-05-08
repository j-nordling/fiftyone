"""
| Copyright 2017-2026, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import re

FO3D_VERSION_KEY = "__FO3D_VERSION"


def camel_to_snake(name):
    """Convert camelCase to snake_case.

    Args:
        name: the camelCase string

    Returns:
        a snake_case string
    ."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


#: Top-level keys whose value is treated as opaque by
#: :func:`convert_keys_to_snake_case`. ``data`` is the
#: :class:`fiftyone.core.threed.plugin_node.PluginNode` payload — its keys
#: are forwarded verbatim to the frontend plugin component, so converting
#: them to snake_case here would break round-tripping (the plugin code
#: keys off the original camelCase).
_OPAQUE_VALUE_KEYS = {"data"}


def convert_keys_to_snake_case(d):
    """Convert all keys in a dictionary from camelCase to snake_case.

    The value of any top-level key in :data:`_OPAQUE_VALUE_KEYS` is
    returned verbatim — its inner keys are *not* converted.

    Args:
        d: the dictionary

    Returns:
        a dictionary with snake case keys
    """
    if isinstance(d, dict):
        return {
            (
                camel_to_snake(k) if k != FO3D_VERSION_KEY else k
            ): (
                v
                if k in _OPAQUE_VALUE_KEYS
                else convert_keys_to_snake_case(v)
            )
            for k, v in d.items()
        }
    elif isinstance(d, list):
        return [convert_keys_to_snake_case(item) for item in d]
    else:
        return d
