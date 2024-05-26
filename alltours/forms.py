from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired

class TourRegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    travel_date = DateField('Travel Date', validators=[DataRequired()])
    travel_time = TimeField('Travel Time', validators=[DataRequired()])
    submit = SubmitField('Register')