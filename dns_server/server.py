import socket
import threading
from dnspython import dns
from dns_server.resolver import DNSResolver
from config import Config

class DNSServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.resolver = DNSResolver()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def start(self):
        self.running = True
        # Bind UDP socket
        self.udp_socket.bind((self.host, self.port))
        # Bind TCP socket
        self.tcp_socket.bind((self.host, self.port))
        self.tcp_socket.listen(5)
        
        print(f"DNS server started on {self.host}:{self.port}")
        
        udp_thread = threading.Thread(target=self._udp_handler)
        tcp_thread = threading.Thread(target=self._tcp_handler))
        
        udp_thread.start()
        tcp_thread.start()
        
        udp_thread.join()
        tcp_thread.join()

    def stop(self):
        self.running = False
        self.udp_socket.close()
        self.tcp_socket.close()

    def _udp_handler(self):
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(512)
                response = self._handle_query(data)
                self.udp_socket.sendto(response, addr)
            except Exception as e:
                print(f"UDP handler error: {e}")

    def _tcp_handler(self):
        while self.running:
            try:
                conn, addr = self.tcp_socket.accept()
                data = conn.recv(1024)
                response = self._handle_query(data)
                conn.send(response)
                conn.close()
            except Exception as e:
                print(f"TCP handler error: {e}")

    def _handle_query(self, data):
        try:
            request = dns.message.from_wire(data)
            response = dns.message.make_response(request)
            
            for question in request.question:
                qname = question.name.to_text()
                qtype = dns.rdatatype.to_text(question.rdtype)
                
                answers = self.resolver.resolve(qname, qtype)
                if answers:
                    for answer in answers:
                        rrset = dns.rrset.from_text(
                            answer['name'],
                            answer['ttl'],
                            answer['class'],
                            answer['type'],
                            answer['data']
                        )
                        response.answer.append(rrset)
                else:
                    # Add SOA record for NXDOMAIN
                    soa = self.resolver.get_soa(qname)
                    if soa:
                        rrset = dns.rrset.from_text(
                            soa['name'],
                            soa['ttl'],
                            soa['class'],
                            soa['type'],
                            soa['data']
                        )
                        response.authority.append(rrset)
                        response.set_rcode(dns.rcode.NXDOMAIN)
            
            return response.to_wire()
        except Exception as e:
            print(f"Query handling error: {e}")
            return dns.message.make_response(dns.message.from_wire(data)).to_wire()