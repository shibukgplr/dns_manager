from webapp.models import Domain, Record
from webapp import db
import dns.resolver
import dns.message
import dns.query
import dns.rdatatype

class DNSResolver:
    ROOT_SERVERS = {
        'a.root-servers.net': '198.41.0.4',
        'b.root-servers.net': '199.9.14.201',
        'c.root-servers.net': '192.33.4.12',
        'd.root-servers.net': '199.7.91.13',
        'e.root-servers.net': '192.203.230.10',
        'f.root-servers.net': '192.5.5.241',
        'g.root-servers.net': '192.112.36.4',
        'h.root-servers.net': '198.97.190.53',
        'i.root-servers.net': '192.36.148.17',
        'j.root-servers.net': '192.58.128.30',
        'k.root-servers.net': '193.0.14.129',
        'l.root-servers.net': '199.7.83.42',
        'm.root-servers.net': '202.12.27.33'
    }

    def __init__(self, recursive=True):
        self.recursive = recursive
        self.cache = {}

    def resolve(self, qname, qtype):
        # Normalize the query name
        qname = qname.rstrip('.').lower()
        
        # First try local resolution
        local_result = self._resolve_local(qname, qtype)
        if local_result:
            return local_result
        
        # If recursive enabled and no local result, try external resolution
        if self.recursive:
            return self._resolve_external(qname, qtype)
        
        return None

    def _resolve_local(self, qname, qtype):
        """Resolve queries from local database"""
        # Check if it's a direct domain match
        domain = Domain.query.filter(Domain.name == qname).first()
        if domain:
            records = self._get_records(domain.id, '@', qtype)
            if records:
                return records
        
        # Check for subdomains
        parts = qname.split('.')
        for i in range(len(parts) - 1):
            subdomain = '.'.join(parts[:i+1])
            parent_domain = '.'.join(parts[i+1:])
            
            domain = Domain.query.filter(Domain.name == parent_domain).first()
            if domain:
                records = self._get_records(domain.id, subdomain, qtype)
                if records:
                    return records
        
        # Check for wildcard records
        domain = Domain.query.filter(Domain.name == '.'.join(parts[1:])).first()
        if domain:
            records = self._get_records(domain.id, '*', qtype)
            if records:
                return [r.replace('*', parts[0]) for r in records]
        
        return None

    def _resolve_external(self, qname, qtype):
        """Recursive resolution using root servers"""
        try:
            # Check cache first
            cache_key = f"{qname}_{qtype}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Start with root servers
            for root_server, ip in self.ROOT_SERVERS.items():
                try:
                    response = self._query_dns(qname, qtype, ip)
                    if response:
                        answers = []
                        for rrset in response.answer:
                            for rr in rrset:
                                answers.append({
                                    'name': qname,
                                    'type': dns.rdatatype.to_text(rrset.rdtype),
                                    'class': 'IN',
                                    'ttl': rrset.ttl,
                                    'data': str(rr)
                                })
                        
                        # Cache the result
                        self.cache[cache_key] = answers
                        return answers
                except Exception as e:
                    continue
            
            return None
        except Exception as e:
            print(f"External resolution error: {e}")
            return None

    def _query_dns(self, qname, qtype, nameserver, timeout=2):
        """Perform a DNS query to a specific nameserver"""
        query = dns.message.make_query(qname, qtype)
        response = dns.query.udp(query, nameserver, timeout=timeout)
        
        if response.rcode() == dns.rcode.NOERROR:
            return response
        return None

    def _get_records(self, domain_id, name, type):
        query = Record.query.filter_by(domain_id=domain_id, name=name)
        if type != 'ANY':
            query = query.filter_by(type=type)
        
        records = query.all()
        if not records:
            return None
        
        result = []
        for record in records:
            data = {
                'name': f"{record.name}.{Domain.query.get(domain_id).name}" if record.name != '@' else Domain.query.get(domain_id).name,
                'type': record.type,
                'class': 'IN',
                'ttl': record.ttl,
                'data': record.content
            }
            result.append(data)
        
        return result

    def get_soa(self, qname):
        parts = qname.split('.')
        for i in range(len(parts)):
            domain_candidate = '.'.join(parts[i:])
            domain = Domain.query.filter(Domain.name == domain_candidate).first()
            if domain:
                soa_record = Record.query.filter_by(
                    domain_id=domain.id,
                    name='@',
                    type='SOA'
                ).first()
                
                if soa_record:
                    return {
                        'name': domain.name,
                        'type': 'SOA',
                        'class': 'IN',
                        'ttl': soa_record.ttl,
                        'data': soa_record.content
                    }
        return None
