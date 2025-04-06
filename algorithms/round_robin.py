class RoundRobin:
  def __init__(self, servers):
    """
    Initialize the Round Robin load balancer with a list of servers.
    :param servers: List of server identifiers (e.g., IP addresses or hostnames)
    """
    self.servers = servers
    self.index = -1

  def get_next_server(self):
    """
    Get the next server in the round robin sequence.
    :return: The next server identifier
    """
    if not self.servers:
      raise ValueError("No servers available")
    
    # Move to the next server in the list
    self.index = (self.index + 1) % len(self.servers)
    return self.servers[self.index]