import unittest
from app import app, db, Client, Tour, Review, Registration, CartItem
import os

class AllToursTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Отключаем CSRF для тестов
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_alltours.db'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.add_test_data()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists('test_alltours.db'):
            os.remove('test_alltours.db')

    def add_test_data(self):
        client = Client(name="Test User", email="testuser@example.com")
        client.password = "testpassword"
        db.session.add(client)
        tour1 = Tour(name="Beach Paradise", description="Enjoy a relaxing vacation on the beautiful beaches of Hawaii.")
        tour2 = Tour(name="Mountain Adventure", description="Experience the thrill of mountain climbing in the Rockies.")
        db.session.add_all([tour1, tour2])
        db.session.commit()

    # Модульные тесты
    def test_register_client(self):
        with app.app_context():
            client = Client(name="New User", email="newuser@example.com")
            client.password = "newpassword"
            db.session.add(client)
            db.session.commit()
            client = Client.query.filter_by(email="newuser@example.com").first()
            self.assertIsNotNone(client)
            self.assertEqual(client.name, "New User")

    def test_add_tour(self):
        with app.app_context():
            tour = Tour(name="New Tour", description="This is a new tour.")
            db.session.add(tour)
            db.session.commit()
            tour = Tour.query.filter_by(name="New Tour").first()
            self.assertIsNotNone(tour)
            self.assertEqual(tour.description, "This is a new tour.")

    def test_add_review(self):
        with app.app_context():
            client = Client.query.first()
            tour = Tour.query.first()
            review = Review(client_id=client.id, tour_id=tour.id, content="Great tour!")
            db.session.add(review)
            db.session.commit()
            review = Review.query.filter_by(content="Great tour!").first()
            self.assertIsNotNone(review)
            self.assertEqual(review.client_id, client.id)

    # Сквозные тесты
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