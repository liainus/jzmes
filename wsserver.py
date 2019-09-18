from constant import constant
from Model.BSFramwork import AlchemyEncoder
import json
import socket
import base64
import hashlib
import redis
import time

# conn = redis.Redis()
# conn.blpop()

def get_headers(data):
    """
    将请求头格式化成字典
    :param data:
    :return:
    """
    header_dict = {}
    data = str(data, encoding='utf-8')
    header, body = data.split('\r\n\r\n', 1)
    header_list = header.split('\r\n')
    for i in range(0, len(header_list)):
        if i == 0:
            if len(header_list[i].split(' ')) == 3:
                header_dict['method'], header_dict['url'], header_dict['protocol'] = header_list[i].split(' ')
        else:
            k, v = header_list[i].split(':', 1)
            header_dict[k] = v.strip()
    return header_dict

def send_msg(conn, msg_bytes):
    """
    WebSocket服务端向客户端发送消息
    :param conn: 客户端连接到服务器端的socket对象,即： conn,address = socket.accept()
    :param msg_bytes: 向客户端发送的字节
    :return:
    """
    import struct

    token = b"\x81"
    length = len(msg_bytes)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)

    msg = token + msg_bytes
    conn.send(msg)
    return True


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('127.0.0.1', 8002))
sock.listen(5)
# 等待用户连接
conn, address = sock.accept()
print('有用户来连接了',conn,address)

data = conn.recv(8096)

headers = get_headers(data) # 提取请求头信息
print('用户发送过来的握手信息',headers['Sec-WebSocket-Key'])

magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
value = headers['Sec-WebSocket-Key'] + magic_string
ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())


response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
      "Upgrade:websocket\r\n" \
      "Connection: Upgrade\r\n" \
      "Sec-WebSocket-Accept: %s\r\n" \
      "WebSocket-Location: ws://%s%s\r\n\r\n"

response_str = response_tpl % (ac.decode('utf-8'), headers['Host'], headers['url'])

conn.send(bytes(response_str, encoding='utf-8'))

while True:
    # info = conn.recv(8096)
    # # 1. 获取第2个字节 content[1] & 127
    # payload_len = info[1] & 127
    # if payload_len == 126:
    #     extend_payload_len = info[2:4]
    #     mask = info[4:8]
    #     decoded = info[8:]
    # elif payload_len == 127:
    #     extend_payload_len = info[2:10]
    #     mask = info[10:14]
    #     decoded = info[14:]
    # else:
    #     extend_payload_len = None
    #     mask = info[2:6]
    #     decoded = info[6:]
    #
    # bytes_list = bytearray()
    # for i in range(len(decoded)):
    #     chunk = decoded[i] ^ mask[i % 4]
    #     bytes_list.append(chunk)
    # body = str(bytes_list, encoding='utf-8')
    # print(body)
    # body = body + ' sb'
    #
    #
    # send_msg(conn,body.encode('utf-8'))

    data_dict = {}
    pool = redis.ConnectionPool(host=constant.REDIS_HOST, password=constant.REDIS_PASSWORD)
    redis_conn = redis.Redis(connection_pool=pool)
    data_dict['CPG'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|JHY_Item01Result').decode('utf-8')
    data_dict['SF'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|JHY_Item02Result').decode('utf-8')
    data_dict['LJ'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|JHY_Item03Result').decode('utf-8')
    data_dict['SF'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|WB_Water').decode('utf-8')
    data_dict['WD'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|WB_Temp').decode('utf-8')
    data_dict['MD'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|WB_MD').decode('utf-8')
    data_dict['ZGY_Temp'] = redis_conn.hget(constant.REDIS_TABLENAME, "t|ZGY_Temp").decode('utf-8')
    data_dict['ZGY_ZGL'] = redis_conn.hget(constant.REDIS_TABLENAME, "t|ZGY_ZGL").decode('utf-8')
    json_data = json.dumps(data_dict, cls=AlchemyEncoder, ensure_ascii=False)
    bytemsg = bytes(json_data, encoding="utf8")

    send_msg(conn, bytemsg)
    time.sleep(2)
sock.close()


if __name__ == '__main__':
    run()