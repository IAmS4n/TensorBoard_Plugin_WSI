from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow.compat.v2 as tf
from tensorboard.compat.proto import summary_pb2

from tensorboard_plugin_wsi import metadata


def wsi(name, path, description=None):
    with tf.summary.experimental.summary_scope(
            name, "greeting_summary", values=[path, 0],
    ) as (tag, _):
        return tf.summary.write(
            tag=tag,
            tensor=tf.constant(path),
            step=0,
            metadata=_create_summary_metadata(description),
        )


def _create_summary_metadata(description):
    return summary_pb2.SummaryMetadata(
        summary_description=description,
        plugin_data=summary_pb2.SummaryMetadata.PluginData(
            plugin_name=metadata.PLUGIN_NAME,
            content=b"",  # no need for summary-specific metadata
        ),
    )
