from webapp.models import Domain, Record
from webapp import db

class DNSResolver:
    def resolve(self, qname, qtype):
        # Normalize the query name
        qname = qname.rstrip('.').lower()
        
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