from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
import tensorflow as tf

from tensorboard_plugin_wsi import summary_v2

tf.compat.v1.enable_eager_execution()
tf = tf.compat.v2


def main(unused_argv):
    writer = tf.summary.create_file_writer("demo_logs")
    with writer.as_default():
        summary_v2.wsi("p1", "~/sample_wsi/1.svs")
        summary_v2.wsi("p2", "~/sample_wsi/2.svs")
        summary_v2.wsi("p3", "~/sample_wsi/3.svs")


if __name__ == "__main__":
    app.run(main)
