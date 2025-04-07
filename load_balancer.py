import socket
from typing import List
from concurrent.futures import ThreadPoolExecutor
from algorithms.round_robin import RoundRobin
from health.health import HealthCheckManager
import logging

logging.basicConfig(
  level=logging.INFO, 
  format='%(asctime)s - %(levelname)s - %(message)s'
)

class LoadBalancer:

  def __init__(self, host="127.0.0.1", port=5050, backend_servers=None, algorithm=None, max_workers=10):
    if backend_servers is None:
      backend_servers = [("127.0.0.1", 8080), ("127.0.0.1", 8081), ("127.0.0.1", 8082)]
    self.host = host
    self.port = port
    self.backends = backend_servers
    self.algorithm = algorithm or RoundRobin(self.backends)
    self.executor = ThreadPoolExecutor(max_workers=max_workers)
    self.health_checker = HealthCheckManager(self.backends)
    self.running = True

  def start(self):
    """
    Start the load balancer and its health check manager.
    """
    health_check_thread = ThreadPoolExecutor(max_workers=1)
    health_check_thread.submit(self.health_checker.start_health_checks)
    logging.info("Health checks started successfully.")

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
  
  def stop(self):
    """
    Stop the load balancer and its health check manager.
    """
    self.running = False
    self.health_checker.stop()
    self.executor.shutdown(wait=True)
    logging.info("Load balancer stopped.")
  
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
  try:
    load_balancer.start()
  except KeyboardInterrupt:
    logging.info("Stopping load balancer...")
    load_balancer.stop()
    logging.info("Load balancer stopped.")