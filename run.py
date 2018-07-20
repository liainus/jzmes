
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
# 导入flask项目
from MES import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5000)  # 对应flask的端口
IOLoop.instance().start()

# 如果要开启多进程模式用下面的代码，不过仅在linux下
# http_server = HTTPServer(WSGIContainer(app))
# http_server.bind(8888)
# http_server.start(0)
# IOLoop.instance().start()
