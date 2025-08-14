import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'WannaTryMyKey_sH1BuKg9lr'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://dnsadmin:Dn5Manage@r@localhost/dns_manager'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True
    DNS_SERVER_HOST = '0.0.0.0'
    DNS_SERVER_PORT = 53
    WEB_INTERFACE_PORT = 5000
    DEFAULT_TTL = 3600