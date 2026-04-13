from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, User, Topic, Comment
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'golos_glubinki_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ГЛАВНАЯ СТРАНИЦА
@app.route('/')
def index():
    return render_template('index.html')


# АВТОРИЗАЦИЯ И РЕГИСТРАЦИЯ (2 в 1 для простоты)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if not user:  # Если нет — регистрируем
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()

        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')


# ПРОСМОТР ТЕМ В КАТЕГОРИИ
@app.route('/category/<cat_name>')
@login_required
def category_topics(cat_name):
    # Фильтруем темы по названию категории
    topics = Topic.query.filter_by(category=cat_name).all()
    return render_template('category_topics.html', cat_name=cat_name, topics=topics)


# СТРАНИЦА ОДНОЙ ТЕМЫ
@app.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
@login_required
def topic_detail(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == 'POST':
        new_comment = Comment(text=request.form.get('text'), topic_id=topic.id, author=current_user.username)
        db.session.add(new_comment)
        db.session.commit()

    comments = Comment.query.filter_by(topic_id=topic_id).all()
    return render_template('topic_detail.html', topic=topic, comments=comments)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаем базу при запуске
    app.run(debug=True)