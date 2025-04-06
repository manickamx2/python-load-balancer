import socket

HELLO_RESPONSE = "Hello from backend server!"

class BackendServer:

  def __init__(self, host="127.0.0.1", port=5050):
    self.host = host
    self.port = port
  
  def start(self):
    addr = (self.host, self.port)
    with socket.socket() as s:
      s.bind(addr)
      s.listen()
      print(f"Backend server listening on {self.host}:{self.port}")
      while True:
        client_socket, address = s.accept()
        print(f"Received connection from {address}")
        self.handle_request(client_socket)
    print(f"Connection closed by client.")
  
  def handle_request(self, client_socket: socket.socket):
    request = client_socket.recv(1024).decode()
    print(f"Received request:\n{request}")

    response = (
      f"HTTP/1.1 200 OK\r\n"
      f"Content-Type: text/plain\r\n"
      f"Content-Length: {len(HELLO_RESPONSE)}\r\n"
      f"\r\n"
      f"{HELLO_RESPONSE}"
    )

    client_socket.sendall(response.encode())
    client_socket.close()


if __name__ == "__main__":

  server = BackendServer()
  server.start()