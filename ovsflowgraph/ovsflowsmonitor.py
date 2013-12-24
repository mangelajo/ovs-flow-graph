# -*- mode: python; coding: utf-8 -*-

__author__ = "Miguel Angel Ajo Pelayo"
__email__ = "miguelangel@ajo.es"
__copyright__ = "Copyright (C) 2013 Miguel Angel Ajo Pelayo"
__license__ = "GPLv3"

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
import ovsflowgraph
import sys

class BridgeMonitor(Resource):

    BRIDGE_MONITOR_HTML = """
                    <html>
                        <head>
                        </head>
                        <body>
                            <img id="dynamicGraph" src="/bridge-graph/test"/>

                            <script>
                            window.setInterval(function()
                            {
                                document.getElementById('dynamicGraph').src =
                                "/bridge-graph/%s?random="+new Date().getTime();
                            }, %d);
                            </script>
                        </body>
                    </html>
                    """
    isLeaf = False

    def getChild(self, name, request):
       return self

    def render_GET(self, request):
        tunnel = None
        reload_ms = 2000
        if len(request.prepath)>1:
            tunnel = request.prepath[1]
        if len(request.prepath)>2:
            reload_ms = int(request.prepath[2])*1000

        if tunnel:
            return self.BRIDGE_MONITOR_HTML % (tunnel,reload_ms)
        else:
            return "No tunnel specified"


class BridgeGraph(Resource):
    isLeaf = False

    def __init__(self):
        self.setFormat('gif')
        Resource.__init__(self)

    def getChild(self, name, request):
       return self

    def setFormat(self, image_format):
        self._image_format = image_format
        if image_format == 'png':
            self._content_type = 'image/png'
        elif image_format == 'svg':
            self._content_type = 'image/svg+xml'
        elif image_format in ['jpg','jpeg']:
            self._content_type = 'image/jpeg'
        else:
            self.setFormat('png')


    def render_GET(self, request):
        tunnel = None
        if len(request.prepath)>1:
            tunnel = request.prepath[1]

        if tunnel:
            request.setHeader('Content-Type', self._content_type)
            return ovsflowgraph.dump_bridge_flows(tunnel,self._image_format)
        else:
            return "No tunnel specified"


class Index(Resource):
    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self,name,request)

    def render_GET(self, request):
        return "<html>Hello, world! %r</html>" %(request.prepath)



def main():

    index = Index()
    bridge_graph = BridgeGraph()
    bridge_monitor = BridgeMonitor()
    index.putChild("bridge-graph",bridge_graph)
    index.putChild("bridge-monitor",bridge_monitor)
    site = Site(index)

    image_format = 'jpg'

    if len(sys.argv)>1:
        image_format = sys.argv[1]

    bridge_graph.setFormat(image_format)

    reactor.listenTCP(8686, site)
    reactor.run()


if __name__ == "__main__":
    main()