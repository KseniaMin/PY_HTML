import unittest
from app import app
from forms import TourRegistrationForm, AddTourForm

class FormsTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_tour_registration_form(self):
        form = TourRegistrationForm(data={
            'full_name': 'Test User',
            'phone_number': '1234567890',
            'travel_date': '2023-12-31',
            'travel_time': '12:00'
        })
        self.assertTrue(form.validate())

    def test_tour_registration_form_missing_full_name(self):
        form = TourRegistrationForm(data={
            'full_name': '',
            'phone_number': '1234567890',
            'travel_date': '2023-12-31',
            'travel_time': '12:00'
        })
        self.assertFalse(form.validate())

    def test_tour_registration_form_invalid_phone_number(self):
        form = TourRegistrationForm(data={
            'full_name': 'Test User',
            'phone_number': 'invalid',
            'travel_date': '2023-12-31',
            'travel_time': '12:00'
        })
        self.assertFalse(form.validate())

if __name__ == '__main__':
    unittest.main()