from spyne import Application
# @rpc decorator exposes methods as remote procedure calls
# and declares the data types it accepts and returns
from spyne import rpc
# spyne.service.ServiceBase is the base class for all service definitions.
from spyne import ServiceBase
# The names of the needed types for implementing this service should be self-explanatory.
from spyne import Iterable, Integer, Unicode

from spyne.protocol.soap import Soap11
# Our server is going to use HTTP as transport, It’s going to wrap the Application instance.
from spyne.server.wsgi import WsgiApplication
import json
from sqlalchemy import String

# step1: Defining a Spyne Service
from Model.BSFramwork import AlchemyEncoder
from spyne import Iterable, Integer, Unicode, Array, util, AnyDict, ModelBase
class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Unicode())
    def WMS_Order_Download(self, name, times):
        dic = []
        for i in range(0,3):
            dic.append(appendStr(i))
        return json.dumps(dic)
def appendStr(i):
    dir = {}
    dir["a"] = str(i)
    dir["b"] = str(i)
    return dir
# step2: Glue the service definition, input and output protocols
soap_app = Application([HelloWorldService], 'spyne.examples.hello.soap',
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11())

# step3: Wrap the Spyne application with its wsgi wrapper
wsgi_app = WsgiApplication(soap_app)

if __name__ == '__main__':
    import logging
    from wsgiref.simple_server import make_server
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://localhost:8000/?wsdl")

    # step4:Deploying the service using Soap via Wsgi
    # register the WSGI application as the handler to the wsgi server, and run the http server
    server = make_server('localhost', 5001, wsgi_app)
    server.serve_forever()
