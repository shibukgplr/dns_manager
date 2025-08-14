from .server import DNSServer
from .resolver import DNSResolver

__all__ = ['DNSServer', 'DNSResolver']

__version__ = '1.0.0'

def create_dns_server(host='0.0.0.0', port=53):

    return DNSServer(host, port)