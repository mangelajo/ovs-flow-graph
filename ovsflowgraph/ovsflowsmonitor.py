# -*- mode: python; coding: utf-8 -*-

__author__ = "Miguel Angel Ajo Pelayo"
__email__ = "miguelangel@ajo.es"
__copyright__ = "Copyright (C) 2013 Miguel Angel Ajo Pelayo"
__license__ = "GPLv3"


from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor


class Graph(Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name=='':
            return self

    def render_GET(self, request):
        return "<html>I'm the bridge %r</html>" %(request.prepath)




class Index(Resource):
    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self,name,request)

    def render_GET(self, request):
        return "<html>Hello, world! %r</html>" %(request.prepath)

index = Index()
bridges = Bridges()
index.putChild("bridges",bridges)

site = Site(index)


reactor.listenTCP(8686, site)
reactor.run()