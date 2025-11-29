from app import create_app, db
from app.models import User

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            u = User(username='admin', email='admin@example.com', role='admin')
            u.set_password('adminpass')
            db.session.add(u)
            db.session.commit()
            print('created admin admin/adminpass')
    app.run(debug=True, port=5000)
