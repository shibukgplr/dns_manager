from webapp import create_app, db
from webapp.models import User, Domain, Record

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='shibukgplr@gmail.com', is_admin=True)
        admin.set_password('admin')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: username=admin, password=P@ssw0rd_wanna_know!") 
    
    print("Database setup complete.")
