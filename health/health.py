import requests
import time
import logging

logging.basicConfig(
  level=logging.INFO, 
  format='%(asctime)s - %(levelname)s - %(message)s'
)

class HealthCheck:
  def __init__(self, url):
    """
    Initialize the HealthCheck class with a URL to monitor.
    :param url: The URL to perform health checks on.
    """
    self.url = url

  def is_healthy(self):
    """
    Perform a health check by sending a GET request to the URL.
    :return: True if the service is healthy (status code 200), False otherwise.
    """
    try:
      response = requests.get(self.url, timeout=5)
      logging.info(f"Health check for {self.url}: {response.status_code}")
      return response.status_code == 200
    except requests.RequestException:
      return False

class HealthCheckManager:
  def __init__(self, backends, health_check_interval=5):
    self.backends = backends
    self.health_check_interval = health_check_interval
    self.healthy_backends = set(backends)
    self.running = True
  
  def start_health_checks(self):
    """
    Periodically check the health of backends and update the list of healthy backends.
    """
    while self.running:
      for backend in self.backends:
        self.check_backend(backend)
      time.sleep(self.health_check_interval)
  
  def check_backend(self, backend):
    """
    Check the health of a single backend server.
    """
    host, port = backend
    health_check = HealthCheck(f"http://{host}:{port}/health/")
    if health_check.is_healthy():
      self.healthy_backends.add(backend)
    else:
      self.healthy_backends.discard(backend)
  
  def get_healthy_backends(self):
    """
    Get the list of currently healthy backends.
    """
    return self.healthy_backends

  def stop(self):
    """
    Stop the health check manager.
    """
    self.running = False