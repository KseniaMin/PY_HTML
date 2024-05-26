from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_migrate import Migrate
from subprocess import Popen, PIPE
from forms import TourRegistrationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alltours.db' # Конфигурация базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Отключение уведомлений об изменениях объектов
app.secret_key = 'supersecretkey'  # Добавьте секретный ключ для использования flash-сообщений

db = SQLAlchemy(app) # Инициализация SQLAlchemy
migrate = Migrate(app, db) # Инициализация Flask-Migrate для управления миграциями базы данных

# Определение моделей
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    reviews = db.relationship('Review', backref='client', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reviews = db.relationship('Review', backref='tour', lazy=True)

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrier = db.Column(db.String(100), nullable=False)
    hotel = db.Column(db.String(100), nullable=False)

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    client = db.relationship('Client', backref='registrations')
    tour = db.relationship('Tour', backref='registrations')
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    travel_time = db.Column(db.Time, nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    tour = db.relationship('Tour')
    client = db.relationship('Client')

# Декоратор для проверки, является ли пользователь администратором
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('You need to be an admin to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Маршруты и функции, Главная страница
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    if search:
        tours = Tour.query.filter(Tour.name.contains(search) | Tour.description.contains(search)).paginate(page=page, per_page=5)
    else:
        tours = Tour.query.paginate(page=page, per_page=5)
    
    return render_template('index.html', tours=tours)

# Детали тура
@app.route('/tour/<int:tour_id>')
def tour_detail(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    return render_template('tour_detail.html', tour=tour)

# Регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_client = Client(name=name, email=email)
        new_client.password = password
        try:
            db.session.add(new_client)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists. Please use a different email address.')
            return redirect(url_for('register'))
    return render_template('register.html')

# Вход пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        client = Client.query.filter_by(email=email).first()
        if client and client.verify_password(password):
            session['client_id'] = client.id
            session['client_name'] = client.name
            session['is_admin'] = client.is_admin
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

# Выход пользователя
@app.route('/logout')
def logout():
    session.pop('client_id', None)
    session.pop('client_name', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# Регистрация на тур
@app.route('/register_tour/<int:tour_id>', methods=['GET', 'POST'])
def register_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    form = TourRegistrationForm()
    if form.validate_on_submit():
        client_id = session.get('client_id')
        if not client_id:
            flash('You need to be logged in to register for a tour.')
            return redirect(url_for('login'))
        full_name = form.full_name.data
        phone_number = form.phone_number.data
        travel_date = form.travel_date.data
        travel_time = form.travel_time.data
        new_registration = Registration(
            client_id=client_id,
            tour_id=tour_id,
            full_name=full_name,
            phone_number=phone_number,
            travel_date=travel_date,
            travel_time=travel_time
        )
        db.session.add(new_registration)
        db.session.commit()
        flash('You have successfully registered for the tour.')
        return redirect(url_for('tour_detail', tour_id=tour_id))
    return render_template('register_tour.html', tour=tour, form=form)

# Добавление тура в корзину
@app.route('/add_to_cart/<int:tour_id>', methods=['POST'])
def add_to_cart(tour_id):
    client_id = session.get('client_id')
    if not client_id:
        flash('You need to be logged in to add items to the cart.')
        return redirect(url_for('login'))
    
    cart_item = CartItem.query.filter_by(client_id=client_id, tour_id=tour_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(client_id=client_id, tour_id=tour_id)
        db.session.add(cart_item)
    db.session.commit()
    flash('Tour added to cart.')
    return redirect(url_for('tour_detail', tour_id=tour_id))

# Просмотр корзины
@app.route('/cart')
def cart():
    client_id = session.get('client_id')
    if not client_id:
        flash('You need to be logged in to view your cart.')
        return redirect(url_for('login'))
    
    cart_items = CartItem.query.filter_by(client_id=client_id).all()
    return render_template('cart.html', cart_items=cart_items)

# Оформление заказа
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    client_id = session.get('client_id')
    if not client_id:
        flash('You need to be logged in to checkout.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Обработать заказ
        CartItem.query.filter_by(client_id=client_id).delete()
        db.session.commit()
        flash('Order placed successfully.')
        return redirect(url_for('index'))
    
    cart_items = CartItem.query.filter_by(client_id=client_id).all()
    return render_template('checkout.html', cart_items=cart_items)

# Добавление отзыва
@app.route('/add_review/<int:tour_id>', methods=['GET', 'POST'])
def add_review(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    if request.method == 'POST':
        client_id = session.get('client_id')
        if not client_id:
            flash('You need to be logged in to add a review.')
            return redirect(url_for('login'))
        content = request.form['content']
        new_review = Review(client_id=client_id, tour_id=tour_id, content=content)
        db.session.add(new_review)
        db.session.commit()
        flash('Review added successfully.')
        return redirect(url_for('tour_detail', tour_id=tour_id))
    return render_template('add_review.html', tour=tour)

# Редактирование отзыва
@app.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    if session.get('client_id') != review.client_id and not session.get('is_admin'):
        flash('You do not have permission to edit this review.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        review.content = request.form['content']
        db.session.commit()
        flash('Review updated successfully.')
        return redirect(url_for('tour_detail', tour_id=review.tour_id))
    
    return render_template('edit_review.html', review=review)

# Удаление отзыва
@app.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if session.get('client_id') != review.client_id and not session.get('is_admin'):
        flash('You do not have permission to delete this review.')
        return redirect(url_for('index'))
    
    tour_id = review.tour_id
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted successfully.')
    return redirect(url_for('tour_detail', tour_id=tour_id))

# Просмотр зарегистрированных туров
@app.route('/my_tours')
def my_tours():
    client_id = session.get('client_id')
    if not client_id:
        flash('You need to be logged in to view your tours.')
        return redirect(url_for('login'))
    registrations = Registration.query.filter_by(client_id=client_id).all()
    tours = [registration.tour for registration in registrations]
    return render_template('my_tours.html', tours=tours)

# Административная панель, Панель администратора
@app.route('/admin')
@admin_required
def admin_dashboard():
    tours = Tour.query.all()
    clients = Client.query.all()
    return render_template('admin_dashboard.html', tours=tours, clients=clients)

# Добавление тура
@app.route('/admin/add_tour', methods=['GET', 'POST'])
@admin_required
def add_tour():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_tour = Tour(name=name, description=description)
        db.session.add(new_tour)
        db.session.commit()
        flash('Tour added successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_tour.html')

# Редактирование тура
@app.route('/admin/edit_tour/<int:tour_id>', methods=['GET', 'POST'])
@admin_required
def edit_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    if request.method == 'POST':
        tour.name = request.form['name']
        tour.description = request.form['description']
        db.session.commit()
        flash('Tour updated successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_tour.html', tour=tour)

# Удаление тура
@app.route('/admin/delete_tour/<int:tour_id>', methods=['POST'])
@admin_required
def delete_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    db.session.delete(tour)
    db.session.commit()
    flash('Tour deleted successfully.')
    return redirect(url_for('admin_dashboard'))

# Редактирование пользователя
@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = Client.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        if 'password' in request.form and request.form['password']:
            user.password = request.form['password']
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_user.html', user=user)

# Удаление пользователя
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = Client.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.')
    return redirect(url_for('admin_dashboard'))

# Запуск тестов
@app.route('/admin/run_tests')
@admin_required
def run_tests():
    process = Popen(['python', '-m', 'unittest', 'discover'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    output = stdout.decode('latin-1') + stderr.decode('latin-1')
    return render_template('run_tests.html', output=output)

# Добавление тестовых данных
def add_test_data():
    if not Tour.query.first():
        tour1 = Tour(name="Beach Paradise", description="Enjoy a relaxing vacation on the beautiful beaches of Hawaii.")
        tour2 = Tour(name="Mountain Adventure", description="Experience the thrill of mountain climbing in the Rockies.")
        tour3 = Tour(name="City Lights", description="Explore the vibrant nightlife of New York City.")
        db.session.add_all([tour1, tour2, tour3])
        db.session.commit()

# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_test_data()
    app.run(debug=True)