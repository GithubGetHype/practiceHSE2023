from app import *

admins = Session.query(Admins).all()

# Выводим admin_id и admin_nickname каждого администратора
print('=================================\n'
        '*            Admins:            *\n'
        '=================================')

for admin in admins:
    print(f'{admin.admin_id} | {admin.admin_nickname} | {admin.admin_email} | {admin.admin_password}')

# Получаем всех пользователей из базы данных
users = Session.query(Users).all()

# Выводим nickname и user_id каждого пользователя
print('=================================\n'
      '*            Users:             *\n'
      '=================================')

for user in users:
    print(f'{user.user_id} | {user.user_nickname} | {user.user_email} | {user.user_balance} | {user.is_block}')

# Получаем все пароли из базы данных
passwords = Session.query(Passwords).all()

# Выводим password_id и password каждого пароля
print("=================================\n"
      "*            Passwords:         *\n"
      "=================================")

for password in passwords:
    print(f'{password.user_id} | {password.password}')

# Получаем все курсы из базы данных
courses = Session.query(Courses).all()

# Выводим course_id, course_name, course_creator и course_count каждого курса
print("=================================\n"
      "*            Courses:           *\n"
      "=================================")

for course in courses:
    print(
        f'{course.course_id} | {course.course_name} | {course.course_text}| {course.course_creator} | {course.course_count} | {course.course_price}')

# Получаем все уроки из базы данных
lessons = Session.query(Lessons).all()

# Выводим lesson_id, course_id, lesson_number, lesson_name, lesson_question и lesson_answer каждого урока
print("=================================\n"
      "*            Lessons:           *\n"
      "=================================")

for lesson in lessons:
    print(
        f'{lesson.lesson_id} | {lesson.course_id} | {lesson.lesson_number} | {lesson.lesson_name} | {lesson.lesson_question} | {lesson.lesson_answer}')

# Получаем все прогресс из базы данных
progress = Session.query(Progress).all()

# Выводим prog_id, user_id, course_id и lesson_id каждого прогресса
print("=================================\n"
      "*            Progress:          *\n"
      "=================================")
print('{prog.prog_id} | {prog.user_id} | {prog.course_id} | {prog.lesson_id}')
for prog in progress:
    print(f'{prog.prog_id} | {prog.user_id} | {prog.course_id} | {prog.lesson_id}')

# Получаем все покупки из базы данных
purchases = Session.query(Purchased).all()

# Выводим purchase_id, user_id, course_id и purchase_date каждой покупки
print("=================================\n"
        "*            Purchases:         *\n"
        "=================================")

for purchase in purchases:
    print(f'{purchase.buy_id} | {purchase.user_id} | {purchase.course_id}')



