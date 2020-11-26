import websocket


def on_message(ws, message):
    print(ws)
    print(message)


def on_error(ws, error):
    print(ws)
    print(error)


def on_close(ws):
    print(ws)
    print("### closed ###")

def on_open(ws):  # 连接到服务器之后就会触发on_open事件，这里用于send数据
    req = '{"event":"subscribe", "channel":"btc_usdt.deep"}'
    print(req)
    ws.send(req)

while True:
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:9200",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(ping_timeout=30)
    # ws.send("Hello, World")##发送消息
    # print("Hello, World")
    # result = ws.recv()##接收消息
    # print(result)
