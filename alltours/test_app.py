import unittest
from app import app, db, Client, Tour, Review, Registration, CartItem

class AllToursTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Отключаем CSRF для тестов
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.add_test_data()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def add_test_data(self):
        client = Client(name="Test User", email="testuser@example.com")
        client.password = "testpassword"
        db.session.add(client)
        tour1 = Tour(name="Beach Paradise", description="Enjoy a relaxing vacation on the beautiful beaches of Hawaii.")
        tour2 = Tour(name="Mountain Adventure", description="Experience the thrill of mountain climbing in the Rockies.")
        db.session.add_all([tour1, tour2])
        db.session.commit()

    def test_register_client(self):
        response = self.app.post('/register', data=dict(
            name='New User', 
            email='newuser@example.com', 
            password='newpassword', 
            confirm='newpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            client = Client.query.filter_by(email='newuser@example.com').first()
            self.assertIsNotNone(client)
            self.assertEqual(client.name, 'New User')

    def test_login(self):
        self.app.post('/register', data=dict(
            name='Test User', 
            email='testuser@example.com', 
            password='testpassword', 
            confirm='testpassword'
        ), follow_redirects=True)
        response = self.app.post('/login', data=dict(
            email='testuser@example.com', 
            password='testpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to AllTours', response.data)

    def test_add_tour(self):
        self.app.post('/register', data=dict(
            name='Admin User', 
            email='admin@example.com', 
            password='adminpassword', 
            confirm='adminpassword'
        ), follow_redirects=True)
        self.app.post('/login', data=dict(
            email='admin@example.com', 
            password='adminpassword'
        ), follow_redirects=True)
        with self.app.session_transaction() as sess:
            sess['is_admin'] = True
        response = self.app.post('/admin/add_tour', data=dict(
            name='New Tour', 
            description='This is a new tour.'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

    def test_add_review(self):
        self.app.post('/register', data=dict(
            name='Test User', 
            email='testuser@example.com', 
            password='testpassword', 
            confirm='testpassword'
        ), follow_redirects=True)
        self.app.post('/login', data=dict(
            email='testuser@example.com', 
            password='testpassword'
        ), follow_redirects=True)
        with self.app.session_transaction() as sess:
            sess['client_id'] = 1
        with app.app_context():
            tour = Tour.query.first()
        response = self.app.post(f'/add_review/{tour.id}', data=dict(
            content='This is a test review.'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tour Details', response.data)

    def test_edit_review(self):
        self.app.post('/register', data=dict(
            name='Test User', 
            email='testuser@example.com', 
            password='testpassword', 
            confirm='testpassword'
        ), follow_redirects=True)
        self.app.post('/login', data=dict(
            email='testuser@example.com', 
            password='testpassword'
        ), follow_redirects=True)
        with self.app.session_transaction() as sess:
            sess['client_id'] = 1
        with app.app_context():
            tour = Tour.query.first()
        self.app.post(f'/add_review/{tour.id}', data=dict(
            content='This is a test review.'
        ), follow_redirects=True)
        with app.app_context():
            review = Review.query.first()
        response = self.app.post(f'/edit_review/{review.id}', data=dict(
            content='This is an edited test review.'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tour Details', response.data)

    def test_delete_review(self):
        self.app.post('/register', data=dict(
            name='Test User', 
            email='testuser@example.com', 
            password='testpassword', 
            confirm='testpassword'
        ), follow_redirects=True)
        self.app.post('/login', data=dict(
            email='testuser@example.com', 
            password='testpassword'
        ), follow_redirects=True)
        with self.app.session_transaction() as sess:
            sess['client_id'] = 1
        with app.app_context():
            tour = Tour.query.first()
        self.app.post(f'/add_review/{tour.id}', data=dict(
            content='This is a test review.'
        ), follow_redirects=True)
        with app.app_context():
            review = Review.query.first()
        response = self.app.post(f'/delete_review/{review.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tour Details', response.data)

    def test_add_to_cart(self):
        self.app.post('/register', data=dict(
            name='Test User', 
            email='testuser@example.com', 
            password='testpassword', 
            confirm='testpassword'
        ), follow_redirects=True)
        self.app.post('/login', data=dict(
            email='testuser@example.com', 
            password='testpassword'
        ), follow_redirects=True)
        with app.app_context():
            tour = Tour.query.first()
        response = self.app.post(f'/add_to_cart/{tour.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tour Details', response.data)

    def test_checkout(self):
        self.app.post('/register', data=dict(
            name='Test User', 
            email='testuser@example.com', 
            password='testpassword', 
            confirm='testpassword'
        ), follow_redirects=True)
        self.app.post('/login', data=dict(
            email='testuser@example.com', 
            password='testpassword'
        ), follow_redirects=True)
        with app.app_context():
            tour = Tour.query.first()
        self.app.post(f'/add_to_cart/{tour.id}', follow_redirects=True)
        response = self.app.post('/checkout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to AllTours', response.data)

if __name__ == '__main__':
    unittest.main()