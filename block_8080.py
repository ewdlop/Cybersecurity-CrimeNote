import socket

def simple_firewall():
    # 建立一個Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 8080))
    s.listen(5)

    while True:
        client, address = s.accept()
        print(f"Connection from {address}")

        # 接收並檢查數據
        data = client.recv(1024)
        if not is_malicious(data):
            client.send(b"Welcome!")
        else:
            client.send(b"Connection blocked!")
        client.close()

def is_malicious(data):
    # 簡單的檢查邏輯
    return b"malicious" in data

if __name__ == "__main__":
    simple_firewall()
