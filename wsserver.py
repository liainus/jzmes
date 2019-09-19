import redis
import json
from constant import constant
from Model.BSFramwork import AlchemyEncoder
import time

from tools.MESLogger import MESLogger

logger = MESLogger('../logs', 'log')
import socket
import struct
import hashlib
import base64
import threading


def get_headers(data):
    headers = {}
    data = str(data, encoding="utf-8")

    header, body = data.split("\r\n\r\n", 1)

    header_list = header.split("\r\n")

    for i in header_list:
        i_list = i.split(":", 1)
        if len(i_list) >= 2:
            headers[i_list[0]] = "".join(i_list[1::]).strip()
        else:
            i_list = i.split(" ", 1)
            if i_list and len(i_list) == 2:
                headers["method"] = i_list[0]
                headers["protocol"] = i_list[1]
    return headers


def parse_payload(payload):
    payload_len = payload[1] & 127
    if payload_len == 126:
        extend_payload_len = payload[2:4]
        mask = payload[4:8]
        decoded = payload[8:]

    elif payload_len == 127:
        extend_payload_len = payload[2:10]
        mask = payload[10:14]
        decoded = payload[14:]
    else:
        extend_payload_len = None
        mask = payload[2:6]
        decoded = payload[6:]

    # 这里我们使用字节将数据全部收集，再去字符串编码，这样不会导致中文乱码
    bytes_list = bytearray()

    for i in range(len(decoded)):
        # 解码方式
        chunk = decoded[i] ^ mask[i % 4]
        bytes_list.append(chunk)
    body = str(bytes_list, encoding='utf-8')
    return body


def send_msg(conn, msg_bytes):
    # 接收的第一字节，一般都是x81不变
    first_byte = b"\x81"
    length = len(msg_bytes)
    if length < 126:
        first_byte += struct.pack("B", length)
    elif length <= 0xFFFF:
        first_byte += struct.pack("!BH", 126, length)
    else:
        first_byte += struct.pack("!BQ", 127, length)

    msg = first_byte + msg_bytes
    conn.sendall(msg)
    return True

sock_pool = []


def handler_accept(sock):

    while True:
        conn, addr = sock.accept()

        data = conn.recv(8096)
        headers = get_headers(data)
        # 对请求头中的sec-websocket-key进行加密
        response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
                       "Upgrade:websocket\r\n" \
                       "Connection: Upgrade\r\n" \
                       "Sec-WebSocket-Accept: %s\r\n" \
                       "WebSocket-Location: ws://%s\r\n\r\n"

        # 第一次连接发回报文
        magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        if headers.get('Sec-WebSocket-Key'):
            value = headers['Sec-WebSocket-Key'] + magic_string

        ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())
        response_str = response_tpl % (ac.decode('utf-8'), headers.get("Host"))
        conn.sendall(bytes(response_str, encoding="utf-8"))
        t = threading.Thread(target=handler_msg, args=(conn, ))
        t.start()


def handler_msg(conn):
        with conn as c:
            data_recv = c.recv(1024)
            while True:
                if data_recv[0:1] == b"\x81":
                    data_parse = parse_payload(data_recv)
                data_dict = {}
                pool = redis.ConnectionPool(host=constant.REDIS_HOST, password=constant.REDIS_PASSWORD)
                redis_conn = redis.Redis(connection_pool=pool)
                data_dict['JHY_CPG'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|JHY_Item01Result').decode('utf-8')
                data_dict['JHY_SF'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|JHY_Item02Result').decode('utf-8')
                data_dict['JHY_LJ'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|JHY_Item03Result').decode('utf-8')
                data_dict['WB_SF'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|WB_Water').decode('utf-8')
                data_dict['WB_WD'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|WB_Temp').decode('utf-8')
                data_dict['WB_MD'] = redis_conn.hget(constant.REDIS_TABLENAME, 't|WB_MD').decode('utf-8')
                data_dict['ZGY_Temp'] = redis_conn.hget(constant.REDIS_TABLENAME, "t|ZGY_Temp").decode('utf-8')
                data_dict['ZGY_ZGL'] = redis_conn.hget(constant.REDIS_TABLENAME, "t|ZGY_ZGL").decode('utf-8')
                json_data = json.dumps(data_dict, cls=AlchemyEncoder, ensure_ascii=False)
                # bytemsg = bytes(json_data, encoding="utf8")
                # send_msg(c, bytes("recv: {}".format(data_parse), encoding="utf-8"))
                bytemsg = bytes(json_data, encoding="utf8")
                send_msg(conn, bytemsg)
                time.sleep(2)



def server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 8002))
    sock.listen(5)
    t = threading.Thread(target=handler_accept(sock))
    t.start()


if __name__ == "__main__":
    server_socket()