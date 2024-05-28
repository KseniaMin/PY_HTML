import unittest
from app import app, db, Client, Tour
from flask import url_for

class ViewsTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test_alltours.db'
        app.config['SERVER_NAME'] = 'localhost'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        with app.app_context():
            db.create_all()
            self.add_test_data()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()

    def add_test_data(self):
        client = Client(name="Test User", email="testuser@example.com")
        client.password = "testpassword"
        db.session.add(client)
        tour1 = Tour(name="Beach Paradise", description="Enjoy a relaxing vacation on the beautiful beaches of Hawaii.")
        tour2 = Tour(name="Mountain Adventure", description="Experience the thrill of mountain climbing in the Rockies.")
        db.session.add_all([tour1, tour2])
        db.session.commit()

    def test_index_view(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to AllTours', response.data)

    def test_tour_detail_view(self):
        with app.app_context():
            tour = Tour.query.first()
        response = self.app.get(url_for('tour_detail', tour_id=tour.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(tour.name.encode(), response.data)

    def test_register_view(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_view(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_logout_view(self):
        with self.app.session_transaction() as sess:
            sess['client_id'] = 1
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to AllTours', response.data)

if __name__ == '__main__':
    unittest.main()