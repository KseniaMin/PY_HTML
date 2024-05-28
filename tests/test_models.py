import unittest
from app import app, db, Client, Tour, Review

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test_alltours.db'
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

    def test_create_client(self):
        with app.app_context():
            client = Client(name="New User", email="newuser@example.com")
            client.password = "newpassword"
            db.session.add(client)
            db.session.commit()
            client = Client.query.filter_by(email="newuser@example.com").first()
            self.assertIsNotNone(client)
            self.assertEqual(client.name, "New User")
        # Проверяет, что можно создать нового клиента и что он присутствует в базе данных.

    def test_create_tour(self):
        with app.app_context():
            tour = Tour(name="New Tour", description="This is a new tour.")
            db.session.add(tour)
            db.session.commit()
            tour = Tour.query.filter_by(name="New Tour").first()
            self.assertIsNotNone(tour)
            self.assertEqual(tour.description, "This is a new tour.")
        # Проверяет, что можно создать новый тур и что он присутствует в базе данных.

    def test_create_review(self):
        with app.app_context():
            client = Client.query.first()
            tour = Tour.query.first()
            review = Review(client_id=client.id, tour_id=tour.id, content="Great tour!")
            db.session.add(review)
            db.session.commit()
            review = Review.query.filter_by(content="Great tour!").first()
            self.assertIsNotNone(review)
            self.assertEqual(review.client_id, client.id)
        # Проверяет, что можно создать новый отзыв и что он присутствует в базе данных.

if __name__ == '__main__':
    unittest.main()