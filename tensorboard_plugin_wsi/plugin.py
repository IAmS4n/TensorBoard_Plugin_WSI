from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
from io import BytesIO

import openslide
import six
import werkzeug
from openslide import open_slide
from openslide.deepzoom import DeepZoomGenerator
from tensorboard.plugins import base_plugin
from tensorboard.util import tensor_util
from werkzeug import wrappers

from tensorboard_plugin_wsi import metadata


class PILBytesIO(BytesIO):
    def fileno(self):
        '''Classic PIL doesn't understand io.UnsupportedOperation.'''
        raise AttributeError('Not supported')


class ExamplePlugin(base_plugin.TBPlugin):
    plugin_name = metadata.PLUGIN_NAME

    def __init__(self, context):
        self._multiplexer = context.multiplexer
        self._cache_slide_prop = []
        self._cache_slide = None
        self._cache_slide_id = None
        self._ids = {}

    def is_active(self):
        return bool(
            self._multiplexer.PluginRunToTagToContent(metadata.PLUGIN_NAME)
        )

    def get_plugin_apps(self):
        return {
            "/index.js": self._serve_js,
            "/tags": self._serve_tags,
            "/slide_prop": self._serve_slide_prop,
            "/tiles/*": self._serve_tiles,
            "/static/*": self._serve_statics,
        }

    @wrappers.Request.application
    def _serve_statics(self, request):
        static_path = request.path[len("/data/plugin/WSI/statics"):]
        filepath = os.path.join(os.path.dirname(__file__), "static", static_path)
        print(filepath)
        if filepath.endswith(".js"):
            with open(filepath) as infile:
                contents = infile.read()
            return werkzeug.Response(
                contents, content_type="application/javascript"
            )
        elif filepath.endswith(".png"):
            with open(filepath, "rb") as infile:
                contents = infile.read()
            response = werkzeug.Response(contents)
            response.headers.set('Content-Type', 'image/png')
            response.headers.set(
                'Content-Disposition', 'attachment', filename=os.path.basename(filepath))
            return response

    def frontend_metadata(self):
        return base_plugin.FrontendMetadata(es_module_path="/index.js")

    @wrappers.Request.application
    def _serve_js(self, request):
        del request  # unused
        filepath = os.path.join(os.path.dirname(__file__), "static", "index.js")
        with open(filepath) as infile:
            contents = infile.read()
        return werkzeug.Response(
            contents, content_type="application/javascript"
        )

    @wrappers.Request.application
    def _serve_tags(self, request):
        del request  # unused
        mapping = self._multiplexer.PluginRunToTagToContent(
            metadata.PLUGIN_NAME
        )
        result = {run: {} for run in self._multiplexer.Runs()}
        for (run, tag_to_content) in six.iteritems(mapping):
            for tag in tag_to_content:
                summary_metadata = self._multiplexer.SummaryMetadata(run, tag)
                result[run][tag] = {
                    u"description": summary_metadata.summary_description,
                }
        contents = json.dumps(result, sort_keys=True)
        return werkzeug.Response(contents, content_type="application/json")

    @wrappers.Request.application
    def _serve_slide_prop(self, request):
        run = request.args.get("run")
        tag = request.args.get("tag")
        runtag = run + tag
        if runtag in self._ids:
            id = self._ids[runtag]
            slide_mpp = self._cache_slide_prop[id]["slide_mpp"]
        else:
            if run is None or tag is None:
                raise werkzeug.exceptions.BadRequest("Must specify run and tag")
            try:
                slide_path = [
                    tensor_util.make_ndarray(event.tensor_proto)
                        .item()
                        .decode("utf-8")
                    for event in self._multiplexer.Tensors(run, tag)
                ][-1]
            except KeyError:
                raise werkzeug.exceptions.BadRequest("Invalid run or tag")

            try:
                slide = open_slide(slide_path)
                mpp_x = slide.properties[openslide.PROPERTY_NAME_MPP_X]
                mpp_y = slide.properties[openslide.PROPERTY_NAME_MPP_Y]
                slide_mpp = (float(mpp_x) + float(mpp_y)) / 2
            except (KeyError, ValueError):
                slide_mpp = 0

            id = len(self._cache_slide_prop)
            self._ids[runtag] = id
            self._cache_slide_prop.append({"slide_path": slide_path, "slide_mpp": slide_mpp})

        data = {"id": id, "mpp": slide_mpp}
        contents = json.dumps(data, sort_keys=True)
        return werkzeug.Response(contents, content_type="application/json")

    @wrappers.Request.application
    def _serve_tiles(self, request):
        tile_config = request.path[len("/data/plugin/WSI/tiles/"):].split("/")

        id = int(tile_config[0])

        if id == self._cache_slide_id:
            slide = self._cache_slide
        else:
            slide_path = self._cache_slide_prop[id]["slide_path"]
            slide = DeepZoomGenerator(open_slide(slide_path))
            self._cache_slide = slide
            self._cache_slide_id = id

        if len(tile_config) <= 2:
            response = werkzeug.Response(slide.get_dzi("jpeg"))
            response.headers.set('Content-Type', 'application/xml')
            return response
        else:
            level, colrow = tile_config[1:]
            level = int(level)
            col, row = map(int, colrow[:-1 * len(".jpeg"):].split("_"))

            tile = slide.get_tile(level, (col, row))

            buf = PILBytesIO()
            tile.save(buf, "jpeg", quality=75)
            response = werkzeug.Response(buf.getvalue())
            response.headers.set('Content-Type', 'image/jpeg')
            return response