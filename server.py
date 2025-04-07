import socket
import argparse

HELLO_RESPONSE = "Hello from backend server!"
HEALTH_CHECK_RESPONSE = "OK"

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
    try:
      request = client_socket.recv(1024).decode()
      print(f"Received request:\n{request}")

      # Parse the HTTP request to determine the requested path
      request_line = request.splitlines()[0]
      method, path, _ = request_line.split()
      print(f"Method: {method}, Path: {path}")

      if method == "GET" and path == "/health/":
        response = (
          f"HTTP/1.1 200 OK\r\n"
          f"Content-Type: text/plain\r\n"
          f"Content-Length: {len(HEALTH_CHECK_RESPONSE)}\r\n"
          f"\r\n"
          f"{HEALTH_CHECK_RESPONSE}"
        )
      elif method == "GET" and path == "/":
        response = (
          f"HTTP/1.1 200 OK\r\n"
          f"Content-Type: text/plain\r\n"
          f"Content-Length: {len(HELLO_RESPONSE)}\r\n"
          f"\r\n"
          f"{HELLO_RESPONSE}"
        )
      else:
        response = (
          f"HTTP/1.1 404 Not Found\r\n"
          f"Content-Type: text/plain\r\n"
          f"Content-Length: 13\r\n"
          f"\r\n"
          f"404 Not Found"
        )
        print(f"Unknown request path: {path}")
      
      # Send the response back to the client
      client_socket.sendall(response.encode())
    except Exception as e:
      print(f"Error processing request: {e}")
    finally:
      client_socket.close()


if __name__ == "__main__":
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description="Start a backend server.")
  parser.add_argument("--port", type=int, default=5050, help="Port to listen on (default: 5050)")
  args = parser.parse_args()

  server = BackendServer(port=args.port)
  server.start()