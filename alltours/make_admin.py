from app import app, db, Client

def make_admin(email):
    with app.app_context():
        user = Client.query.filter_by(email=email).first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f"User {email} is now an admin.")
        else:
            print(f"User {email} not found.")

if __name__ == '__main__':
    email = input("Введите адрес электронной почты пользователя, чтобы стать администратором: ")
    make_admin(email)