from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import setuptools

setuptools.setup(
    name="tensorboard_plugin_wsi",
    version="0.1.0",
    description="A TensorBoard plugin to view WSI images.",
    packages=["tensorboard_plugin_wsi"],
    package_data={"tensorboard_plugin_wsi": ["static/**"], },
    entry_points={
        "tensorboard_plugins": [
            "example_basic = tensorboard_plugin_wsi.plugin:ExamplePlugin",
        ],
    },
)
