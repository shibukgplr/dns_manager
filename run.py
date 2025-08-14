from dns_server.server import DNSServer
from webapp import create_app
from config import Config
import threading

def run_dns_server():
    # Enable recursive resolution (set False for authoritative-only)
    dns_server = DNSServer(
        Config.DNS_SERVER_HOST, 
        Config.DNS_SERVER_PORT, 
        recursive=True  # Change to False to disable recursive resolution
    )
    dns_server.start()

def run_web_app():
    app = create_app()
    app.run(host='0.0.0.0', port=Config.WEB_INTERFACE_PORT)

if __name__ == '__main__':
    # Start DNS server in a separate thread
    dns_thread = threading.Thread(target=run_dns_server)
    dns_thread.daemon = True
    dns_thread.start()
    
    # Start web application
    run_web_app()