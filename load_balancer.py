import socket
from typing import List
from concurrent.futures import ThreadPoolExecutor
from algorithms.round_robin import RoundRobin

class LoadBalancer:

  def __init__(self, host="127.0.0.1", port=5050, backend_servers=None, algorithm=None, max_workers=10):
    if backend_servers is None:
      backend_servers = [("127.0.0.1", 8080), ("127.0.0.1", 8081), ("127.0.0.1", 8082)]
    self.host = host
    self.port = port
    self.backends = backend_servers
    self.algorithm = algorithm or RoundRobin(self.backends)
    self.executor = ThreadPoolExecutor(max_workers=max_workers)

  def start(self):
    addr = (self.host, self.port)
    with socket.socket() as s:
      s.bind(addr)
      s.listen()
      print(f"Load balancer listening on {self.host}:{self.port}")
      while True:
        client_socket, address = s.accept()
        print(f"Received request from {address}")
        # Submit the request to the executor thread pool for handling
        self.executor.submit(self.handle_request, client_socket)
    print(f"Connection closed by client.")
  
  def handle_request(self, client_socket: socket.socket):
    try:
      backend = self.algorithm.get_next_server()
      self.forward_request(client_socket, backend)
    except Exception as e:
      print(f"Error handling client request: {e}")
    finally:
      client_socket.close()
      print(f"Client socket closed.")
  
  def forward_request(self, client_socket: socket.socket, backend_addr: tuple):
    with socket.socket() as backend_socket:
      backend_socket.connect(backend_addr)
      request = client_socket.recv(2048)
      if not request:
        print(f"Did not receive a valid request")
        return
      print(f"{request.decode()}")
      
      backend_socket.sendall(request)
      response = backend_socket.recv(2048)

      status = self.parse_response(response.decode())[0]
      print(f"Response from server: {status}")
    
      client_socket.sendall(response)
      client_socket.close()
  
  def parse_response(self, response: str) -> List:
    response_arr = response.split('\r\n')
    return response_arr
    
  

if __name__ == "__main__":

  load_balancer = LoadBalancer(max_workers=10)
  load_balancer.start()