from webapp import create_app, db
from webapp.models import User, Domain, Record

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: username=admin, password=admin")  //setup your creds
    
    print("Database setup complete.")