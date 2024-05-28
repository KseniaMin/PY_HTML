import unittest
from app import app, db, Tour

class TourTestCase(unittest.TestCase):
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
        tour1 = Tour(name="Beach Paradise", description="Enjoy a relaxing vacation on the beautiful beaches of Hawaii.")
        tour2 = Tour(name="Mountain Adventure", description="Experience the thrill of mountain climbing in the Rockies.")
        db.session.add_all([tour1, tour2])
        db.session.commit()

    def test_tour_count(self):
        with app.app_context():
            tours = Tour.query.all()
            self.assertEqual(len(tours), 2, "Tour count is not as expected.")

if __name__ == '__main__':
    unittest.main()