# dns_managr
Custom DNS server with a web interface using Python, Flask, and MariaDB.


dns-server/
│
├── dns_server/              
│   ├── __init__.py
│   ├── server.py             
│   └── resolver.py          
│

├── webapp/                   
│   ├── __init__.py
│   ├── models.py             
│   ├── routes.py             
│   ├── templates/            
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── domain.html
│   │   ├── add_domain.html
│   │   ├── add_record.html
│   │   └── edit_record.html
│   ├── static/               
│   │   └── style.css
│   └── auth.py               
│

├── config.py                 
├── requirements.txt          
├── setup_database.py         
└── run.py                    
