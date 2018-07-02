from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from MicroMES import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5000,'127.0.0.1')  #flask默认的端口,可任意修改
IOLoop.instance().start()
