import tensorflow as tf
from tensorboard_plugin_wsi import summary_v2

tf.compat.v1.enable_eager_execution()
tf = tf.compat.v2

writer = tf.summary.create_file_writer("demo_logs")
with writer.as_default():
    summary_v2.wsi("wsi_1", "Path to a wsi file")
    summary_v2.wsi("wsi_2", "Path to a wsi file")