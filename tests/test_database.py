import unittest
import os
from app import app, db, Client, Tour

class DatabaseTestCase(unittest.TestCase):
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
        tour1 = Tour(name="Beach Paradise", description="Enjoy a relaxing vacation on the beautiful beaches of Hawaii.", image_url="path/to/image1.jpg")
        tour2 = Tour(name="Mountain Adventure", description="Experience the thrill of mountain climbing in the Rockies.", image_url="path/to/image2.jpg")
        db.session.add_all([tour1, tour2])
        db.session.commit()

    def test_database_exists(self):
        self.assertTrue(os.path.exists('instance/test_alltours.db'), "Database does not exist.")

    def test_clients_exist(self):
        with app.app_context():
            clients = Client.query.all()
            self.assertTrue(len(clients) > 0, "No clients found in the database.")

    def test_tours_exist(self):
        with app.app_context():
            tours = Tour.query.all()
            self.assertTrue(len(tours) > 0, "No tours found in the database.")

    def test_images_exist(self):
        with app.app_context():
            tours = Tour.query.all()
            images_exist = all(tour.image_url for tour in tours)
            self.assertTrue(images_exist, "Not all tours have images.")

if __name__ == '__main__':
    unittest.main()