from flask import Flask, render_template, redirect, url_for, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import session
import bcrypt
import datetime
from sqlalchemy.sql.functions import current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

# Создание базы данных
engine = create_engine('sqlite:///users.db', echo=True)

# Создание объекта базы данных
Base = declarative_base()


# Определение класса Admins и его таблицы в базе данных
class Admins(Base):
    __tablename__ = 'admins'
    admin_id = Column(Integer, primary_key=True)
    admin_nickname = Column(String, unique=True)
    admin_email = Column(String, unique=True)
    admin_password = Column(String)


# Определение класса Users и его таблицы в базе данных
class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_nickname = Column(String, unique=True)
    user_email = Column(String, unique=True)
    user_balance = Column(Integer, default=0)
    is_block = Column(Integer, default=False)
    password = relationship("Passwords", uselist=False, back_populates="user")


# Определение класса Passwords и его таблицы в базе данных
class Passwords(Base):
    __tablename__ = 'passwords'
    pas_id = Column(Integer, primary_key=True)
    password = Column(String)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("Users", back_populates="password")


class Courses(Base):
    __tablename__ = 'courses'
    course_id = Column(Integer, primary_key=True)
    course_name = Column(String)
    course_creator = Column(String, ForeignKey('users.user_nickname'))
    course_count = Column(Integer)
    course_text = Column(String)  # новый столбец
    course_price = Column(Integer, default=0)


class Lessons(Base):
    __tablename__ = 'lessons'
    lesson_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.course_id'))
    lesson_number = Column(Integer)
    lesson_name = Column(String)
    lesson_question = Column(String)
    lesson_answer = Column(String)


class Progress(Base):
    __tablename__ = 'progress'
    prog_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    course_id = Column(Integer, ForeignKey('courses.course_id'))
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id'))

    user = relationship("Users", backref="progress")
    course = relationship("Courses", backref="progress")
    lesson = relationship("Lessons", backref="progress")


class Purchased(Base):
    __tablename__ = 'purchased'
    buy_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    course_id = Column(Integer, ForeignKey('courses.course_id'))

    user = relationship("Users", backref="purchased")
    course = relationship("Courses", backref="purchased")


# Создание таблиц в базе данных
Base.metadata.create_all(engine)

# Создание объекта сессии для взаимодействия с базой данных
Session = scoped_session(sessionmaker(bind=engine))


# Отображаем login.html при запуске приложения
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/registration', methods=['POST'])
def registration_post():
    # Получаем данные из полей nickname, email и password
    nick = request.form['nickname']
    email = request.form['email']
    password = request.form['password']
    if 'user-type' in request.form:
        user_type = request.form['user-type']
        if user_type == 'on':
            admin_nickname = Session.query(Admins).filter_by(admin_nickname=nick).first()
            admin_email = Session.query(Admins).filter_by(admin_email=email).first()
            if admin_nickname or admin_email:
                return render_template('registration.html', error_already=True)
            else:
                if (len(nick) > 3) and (len(email) > 4 and '@' in email and '.' in email) and len(password) >= 3:
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
                    new_admin = Admins(admin_nickname=nick, admin_email=email, admin_password=hashed_password)
                    Session.add(new_admin)
                    Session.commit()
                    return render_template('login.html')
                else:
                    return render_template('registration.html', error=True)
    else:
        user_nickname = Session.query(Users).filter_by(user_nickname=nick).first()
        user_email = Session.query(Users).filter_by(user_email=email).first()
        if user_nickname or user_email:
            return render_template('registration.html', error_already=True)
        else:
            if (len(nick) > 3) and (len(email) > 4 and '@' in email and '.' in email) and len(password) >= 3:
                # Хеширование пароля с помощью библиотеки bcrypt
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

                # Добавляем пользователя в базу данных
                new_user = Users(user_nickname=nick, user_email=email)
                new_password = Passwords(password=hashed_password)
                new_user.password = new_password
                Session.add(new_user)
                Session.commit()
                user_id = new_user.user_id
                return render_template('login.html')
            else:
                return render_template('registration.html', error=True)


@app.route('/admin/<int:admin_id>')
def admin(admin_id):
    admin = Session.query(Admins).filter_by(admin_id=admin_id).first()
    # Получаем все балансы пользователей из базы данных
    users = Session.query(Users).all()
    users_balance = [{'user_id':user.user_id, 'nickname': user.user_nickname, 'balance': user.user_balance, 'is_block': user.is_block} for user in users]
    return render_template('admin.html', admin=admin, users_balance=users_balance)

@app.route('/admin', methods=['POST'])
def admin_post():
    if 'add' in request.form:
        user_id = request.form['user_id']
        add_balance = request.form['add_balance']
        user = Session.query(Users).filter_by(user_id=user_id).first()
        user.user_balance += int(add_balance)
        Session.commit()
        return redirect(url_for('admin', admin_id=session['admin_id'], ready=True))
    elif 'block' in request.form:
        user = Session.query(Users).filter_by(user_id=request.form['user_id']).first()
        user.is_block = True
        Session.commit()
        return redirect(url_for('admin', admin_id=session['admin_id'], ready=True))
    elif 'unblock' in request.form:
        user = Session.query(Users).filter_by(user_id=request.form['user_id']).first()
        user.is_block = False
        Session.commit()
        return redirect(url_for('admin', admin_id=session['admin_id'], ready=True))

@app.route('/main/<int:user_id>')
def main(user_id):
    user = Session.query(Users).filter_by(user_id=user_id).first()
    # Получаем баланс пользователя из базы данных
    user_balance = user.user_balance
    # Получаем список курсов из базы данных
    courses = Session.query(Courses).all()
    courses_list = [{'name': course.course_name, 'creator': course.course_creator, 'id': course.course_id, 'pr': course.course_price} for course in courses]
    # Добавляем параметр id в список курсов
    return render_template('main.html', courses=courses_list, user=user, user_balance=user_balance)


# Обработчик POST-запроса на страницу /login
@app.route('/login', methods=['POST'])
def login_post():
    # Получаем данные из полей nickname_user и password
    nickname = request.form['nickname_user']
    password_check = request.form['password']

    # Проверяем, есть ли пользователь с таким никнеймом в базе данных
    user = Session.query(Users).filter_by(user_nickname=nickname).first()
    admin = Session.query(Admins).filter_by(admin_nickname=nickname).first()
    if user and not user.is_block:
        # Проверяем, совпадает ли хеш пароля из базы данных с хешем введенного пароля
        if bcrypt.checkpw(password_check.encode('utf-8'), user.password.password):
            session['user_id'] = user.user_id
            return redirect(url_for('main', user_id=session['user_id']))
    elif user and user.is_block:
        return redirect(url_for('block', user_id=session['user_id']))
    elif admin:
        if bcrypt.checkpw(password_check.encode('utf-8'), admin.admin_password):
            session['admin_id'] = admin.admin_id
            return redirect(url_for('admin', admin_id=session['admin_id']))
    else:
        return render_template('login.html', error=True)



@app.route('/block')
def block():
    return render_template('block.html')


# Отображаем registration.html при клике на "Don't have an account yet?"
@app.route('/registration')
def registration():
    return render_template('registration.html')


# Отображаем login.html при клике на "Already have an account?"
@app.route('/login')
def back_to_login():
    return render_template('login.html')


@app.route('/course/<int:course_id>')
def course(course_id):
    # Получаем объект курса из базы данных
    course = Session.query(Courses).filter_by(course_id=course_id).first()
    # Получаем сourse_text из базы данных
    course_text = course.course_text
    # Создаем словарь данных для передачи в шаблон course.html
    data = {
        'name': course.course_name,
        'creator': course.course_creator
    }

    # получаем все данные из таблицы Lessons
    lessons = Session.query(Lessons).filter_by(course_id=course_id).all()

    # создаем список словарей с данными из таблицы Lessons
    lessons_list = [{'id': lesson.lesson_id, 'number': lesson.lesson_number, 'name': lesson.lesson_name,
                     'question': lesson.lesson_question, 'answer': lesson.lesson_answer} for lesson in lessons]

    return render_template('course.html', **data, lessons=lessons_list, course_text=course_text)


@app.route('/my_courses/<int:user_id>')
def my_courses(user_id):
    # Получаем объект пользователя из базы данных
    user = Session.query(Users).filter_by(user_id=user_id).first()
    # Создаем список курсов, которые создал пользователь
    courses = Session.query(Courses).filter_by(course_creator=user.user_nickname).all()
    courses_list = [{'name': course.course_name, 'creator': course.course_creator, 'id': course.course_id} for course in courses]

    return render_template('my_courses.html', courses=courses_list, user=user)


@app.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    # Получаем объект курса из базы данных
    course = Session.query(Courses).filter_by(course_id=course_id).first()
    user = session.get('user_id')
    # Удаляем курс из базы данных
    Session.delete(course)

    # Получаем список уроков, связанных с курсом
    lessons = Session.query(Lessons).filter_by(course_id=course_id).all()

    # Удаляем все уроки, связанные с курсом
    for lesson in lessons:
        Session.delete(lesson)

    # Сохраняем изменения в базе данных
    Session.commit()

    # Возвращаем пользователя на страницу с его курсами
    return 'Course deleted'


@app.route('/add_course/<int:user_id>')
def add_course(user_id):
    return render_template('add_course.html', user_id=user_id)


@app.route('/add_course', methods=['POST'])
def add_coursea():
    user_id = session.get('user_id')
    user = Session.query(Users).filter_by(user_id=user_id).first()
    # print(user_id, user.user_nickname)
    course_price = request.form.get('course_price')
    course_name = request.form.get('course_name')
    course_text = request.form.get('course_text')
    lessons_c = request.form.get('lessons')

    lesson_names = request.form.getlist('lesson_name')
    lesson_texts = request.form.getlist('lesson_text')
    lesson_answers = request.form.getlist('lesson_answer')
    if 'add_course' in request.form:
        # проверяем что нет пустых значений и что значение course_price является числом и что lessons больше 0
        if not course_price or not course_name or not course_text or not lessons_c or not lesson_names or not lesson_texts or not lesson_answers or not course_price.isdigit() or int(lessons_c) <= 0:
            return 'Ошибка ввода данных!'
        else:
            # Добавляем название, текст, user.user_nickname, lessons курса в таблицу Courses
            course = Courses(course_name=course_name, course_text=course_text, course_creator=user.user_nickname, course_count=lessons_c, course_price=course_price)
            Session.add(course)
            Session.commit()
            # Добавляем id курса, id урока в этом курсе, название, вопрос и ответ урока в таблицу Lessons
            for i in range(int(lessons_c)):
                lesson = Lessons(course_id=course.course_id, lesson_number=i + 1, lesson_name=lesson_names[i],
                                 lesson_question=lesson_texts[i], lesson_answer=lesson_answers[i])
                Session.add(lesson)
                Session.commit()
            return 'Курс зарегистрирован!'


@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    # получаем номер урока в который ввели ответ
    lesson_number = request.form.get('lesson_number')
    # получаем id курса в который ввели ответ из таблицы Lessons
    course_id = Session.query(Lessons).filter_by(lesson_id=lesson_number).first().course_id
    print(course_id)
    # проверяем есть ли такой курс у этого пользователя в таблице Purchased и если нет и баланса хватает, то добавляем курс в таблицу Purchased, а если нет то выводим ошибку
    user_id = session.get('user_id')
    user = Session.query(Users).filter_by(user_id=user_id).first()
    course = Session.query(Courses).filter_by(course_id=course_id).first()
    if not Session.query(Purchased).filter_by(user_id=user_id, course_id=course_id).first():
        if user.user_balance >= course.course_price:
            user.user_balance -= course.course_price
            # Перезаписать значение баланса в базе данных
            purchased = Purchased(user_id=user_id, course_id=course_id)
            Session.add(purchased)
            Session.commit()
            return 'Курс успешно куплен!'
        else:
            return 'Not enough money'
    else:
        answer = request.form.get('answer')

        # Получаем ответ на вопрос lesson_number и сравниваем его с ответом пользователя
        lesson = Session.query(Lessons).filter_by(lesson_id=lesson_number).first()

        if lesson.lesson_answer == answer:
            # добавляем правильный ответ в таблицу Results для пользователя с id user_id и курса с id course_id и lesson_number
            user_id = session.get('user_id')
            # получаем course_id из таблицы Lessons по lesson_number
            course_id = Session.query(Lessons).filter_by(lesson_id=lesson_number).first().course_id
            result = Progress(user_id=user_id, course_id=course_id, lesson_id=lesson_number)
            # Проверяем что такого ответа еще нет в таблице Results
            if not Session.query(Progress).filter_by(user_id=user_id, course_id=course_id, lesson_id=lesson_number).first():
                Session.add(result)
                Session.commit()
                result = f'Вопрос {lesson_number}: {answer} - правильно! Ответ добавлен!'
            else:
                result = f'Вопрос {lesson_number}: {answer} - правильно! Ответ уже был!'
        else:
            result = f'Вопрос {lesson_number}: {answer} - неправильно!'
        return result


# Получаем список записей из таблицы Progress
progress = Session.query(Progress).all()
# Удаляем запись из таблицы Progress, если в ней есть None
for record in progress:
    if record.user_id is None or record.course_id is None or record.lesson_id is None:
        Session.delete(record)
        Session.commit()


# Переход на страницу с прогрессом пользователя по курсу
@app.route('/my_progress/<int:user_id>')
def progress(user_id):
    # Получаем объект пользователя из базы данных
    user = session.get('user_id')
    # Получаем список записей из таблицы Progress
    progress = Session.query(Progress).all()
    # Удаляем запись из таблицы Progress, если в ней есть None
    for record in progress:
        if record.user_id is None or record.course_id is None or record.lesson_id is None:
            Session.delete(record)
            Session.commit()
    # Получаем список course_id курсов из базы данных Progress по user_id, которые начал выполнять пользователь
    answers = Session.query(Progress).filter_by(user_id=user_id).all()
    answers_list = [{'course_id': answer.course_id, 'lesson_id': answer.lesson_id} for answer in answers]

    return render_template('my_progress.html', user=user, answers_list=answers_list)


@app.route('/mainn', methods=['POST'])
def add_balance():
    balance = request.form['add_balance']
    # Добавить сумму к балансу пользователя
    user_id = session.get('user_id')
    user = Session.query(Users).filter_by(user_id=user_id).first()
    try:
        user.user_balance += int(balance)
        Session.commit()
    except:
        return "Неверный формат суммы!"
    return "Сумма добавлена!"


if __name__ == '__main__':
    app.run(debug=True, port=5002)
