import random
import sqlite3
from flask import Flask, render_template, g, request, session, redirect, url_for, flash, get_flashed_messages
from flask import Flask, make_response, render_template_string
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timedelta
from functools import wraps
from models import db
from models import User
from models import Administrator
from models import Member
from models import Mercenary
from models import Certificate
from models import Task
from models import Report
import os
import base64
import json


# нужно настроить журнал посещений так, 
# чтобы пользователь мог смотреть только свои записи, 
# а админ мог просматривать записи всех пользователей.


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Course.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Настройка: папка для сохранения изображений (создайте её вручную или код создаст)
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

# Разрешаем большие файлы (опционально)
# app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024  # 16 MB

# Обозначаем ограничение памяти, на которое можно загружать картинки в отчёт.
app.config['MAX_FORM_MEMORY_SIZE'] = 256 * 1024 * 1024  # 256 МБ на текстовые поля формы (base64)

DATABASE = "Course.db"

db.init_app(app)

application = app

with app.app_context():
    db.create_all()  

# <!-- Механизмы аутентификации -->

login_manager = LoginManager() # Создаётся менеджер login_manager, который управляет всем, что связано с сессиями пользователей.
login_manager.init_app(app) # Менеджер привязывается к текущему приложению
login_manager.login_view = 'authentication'  #Обозначаем, что функция authentication отвечает за авторизацию

application = app

#Сообщение, появляющееся, если вы не прошли авторизацию
@login_manager.unauthorized_handler
def unauthorized():
    flash("Пройдите процедуру авторизации, чтобы получить доступ к странице.", "danger")
    return redirect(url_for('authentication'))

#Выход из системы
@app.route('/goout', methods=['GET', 'POST'])
def goout():
    if request.method == 'POST':
        logout_user()
        flash("Вы вышли из системы, повторно пройдите автоизацию!", "success")
        return redirect(url_for('main_page'))
    return render_template('main_pages/main_page.html', title='Авторизация')

#Функция для проверки ролей
def check_rights(roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            # Если не удалось зайти на страницу, то об этом не будет создаваться запись в БД.
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("У вас недостаточно прав для доступа к данной странице.", "danger")
                return redirect(url_for('main_page'))

            # 1. Проверка авторизации
            if not current_user.is_authenticated:
                flash("Сначала войдите в систему", "danger")
                return redirect(url_for('authentication'))

            # 2. Проверка роли
            if current_user.role not in roles:
                flash("У вас недостаточно прав для доступа к данной странице.", "danger")
                return redirect(url_for('main_page'))

            # 3. Всё ок → выполняем функцию
            return f(*args, **kwargs)

        return wrapper
    return decorator

# Загрузка пользователя, если он проходил авторизацию
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Действия, выполняемые перед запросом.
# Если пользователь был зарегестрирован, 
# то его находят по id в БД и подгружают его данные в БД

@app.before_request
def before_request():
    #g.db = get_db()
    if current_user.is_authenticated:
        user_id = int(current_user.id)
    else:
        user_id = None
        
# Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
def auth():
    if current_user.is_authenticated:
        return current_user.role
    else:
        return "none"
    


# <!-- Завершение блока "Механизмы аутентификации" -->

# <!-- Аутентификация -->

# <!-- authentication.html - Страница авторизации в систему -->
@app.route('/authentication/', methods=['GET', 'POST'])
def authentication():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    now = datetime.now().date() # Сегодняшняя дата

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        userdata = User.query.filter_by(username=username, password=password).first()

        if (userdata and check_password_hash(userdata.password, password)) or userdata:
            login_user(userdata)
            if current_user.role == "mercenary":
                mercenary_tasks = Task.query.filter_by(id_mercenary=current_user.id, status_task="in_process").all()
                Inactive = False
                for task in mercenary_tasks:
                    if (task.doing_task + timedelta(days=7) < now and task.end_of_task==None):
                        Inactive = True
                if Inactive:
                    current_user.mercenary.status_mercenary = "Inactive"
                    flash(f"Вы не выполнили ваше задание за отведенный срок, а поэтому ваш статус сменён на Inactive и вы не отображаетесь в списке наёмников. Если вы не сможете выполнить текущее задание или выполнить новое, то о вас забудут и вы потеряете известность и ваша карьера будет разрушена.", "danger")
                    db.session.commit()
                else:
                    current_user.mercenary.status_mercenary = "Alive"
                    db.session.commit()



            flash(f"Вы успешно зарегестрировались на сайте!", "success")
            return redirect(url_for('main_page'))
        else:
            flash(f"Вы неправильно ввели данные, попробуйте ещё раз {username} {password}", "danger")
            return redirect(url_for('authentication'))

    return render_template('auth/authentication.html', user_role=user_role)



# <!-- create_member.html - Страница создания записи представителя -->
@app.route('/create_member/', methods=['GET', 'POST'])
def create_member():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        organization_name = request.form.get('organization_name')
        organization_code = request.form.get('organization_code')
        userdata = User.query.filter_by(username=username).first()
        now = datetime.now().date() # Дата регистрации
        if (organization_name == "Empire" and organization_code == "empire123") or (organization_name == "Bird" and organization_code == "bird123") or (organization_name == "Front" and organization_code == "front123"):

        #Механизм автоматического присвоения роли прописан в models.py

            if (not userdata): #НУЖДАЕТСЯ В ИСПРАВЛЕНИИ
                try:
                    new_user = User( # Создаём новую запись в таблице User
                        username = username, 
                        password = password, 
                        registration_date = now
                    )

                    db.session.add(new_user)
                    db.session.flush()              # БД присваивает id, но транзакция ещё не закрыта

                    # теперь new_user.id уже доступен
                    new_member = Member(
                        id_member=new_user.id, 
                        fraction=organization_name,
                        fraction_code=organization_code
                    )   # используем его как внешний ключ
                    db.session.add(new_member)
                    db.session.commit()   
                    flash("Успешно добавлена новая запись", "success")
                    return redirect(url_for('authentication'))
                except Exception as e:
                    flash("Ошибка:" + str(e), "danger")

                flash(f"Вы успешно зарегестрировались на сайте!", "success")
                return redirect(url_for('main_page'))
            else:
                flash(f"Вы неправильно ввели данные, попробуйте ещё раз", "danger")
                return redirect(url_for('create_member'))
            
    return render_template('auth/create_member.html', user_role=user_role)






# <!-- create_mercenary.html - Страница создания личного кабинета наёмника -->
@app.route('/create_mercenary/', methods=['GET', 'POST'])
def create_mercenary():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        telegram = request.form.get('telegram')
        certificate_code  = request.form.get('cert')
        userdata = User.query.filter_by(username=username).first()
        certificate = Certificate.query.filter_by(certificate_code=certificate_code).first()
        used_certificate = Mercenary.query.filter_by(certificate_code=certificate_code).first()

        now = datetime.now().date()

        #Механизм автоматического присвоения роли прописан в models.py

        if (not userdata and certificate and not used_certificate):
            try:
                new_user = User(
                    username = username, 
                    password = password, 
                    registration_date = now
                )
                db.session.add(new_user)
                db.session.flush() 

                new_mercenary = Mercenary(
                    id_mercenary=new_user.id, 

                    telegram_username=telegram,
                    certificate_code=certificate.certificate_code,
                    rating_mercenary=0,
                    status_mercenary="Alive",
                    favourite_fraction="none",
                    price_mercenary=0
                )
                db.session.add(new_mercenary)
                db.session.commit() 

                flash("Успешно добавлена новая запись", "success")
                data = User.query.all()
                return redirect(url_for('authentication'))
            except Exception as e:
                flash("Ошибка:" + str(e), "danger")

            flash(f"Вы успешно зарегестрировались на сайте!", "success")
            return redirect(url_for('main_page'))
        else:
            flash(f"Вы неправильно ввели данные, попробуйте ещё раз", "danger")
            return redirect(url_for('create_mercenary'))
        
    return render_template('auth/create_mercenary.html', user_role=user_role)



# <!-- Главные страницы -->

# <!-- main_page.html - Главная страница сайта, на которую все заходят при входе на сайт -->
@app.route('/')
def main_page():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    page = request.args.get('page', 1, type=int)
    
    pagination = (Task.query.filter_by(status_task="Active").order_by(Task.rating_task.desc()).paginate(
        page=page,
        per_page=2,
        error_out=False)   
    )

    tasks = pagination.items

    return render_template('main_pages/main_page.html', user_role=user_role, tasks=tasks, pagination=pagination)

# <!-- Механизмы main_page -->

# task_accept - функция-подтверждение того, что вы взяли задание и оно у вас активное
@app.route('/task_accept/<int:id_task>/')
@check_rights(["mercenary"])
def task_accept(id_task):
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    task = Task.query.filter_by(id_task=id_task).first()

    now = datetime.now().date()

    if task and user_role == "mercenary":
        task.status_task = "in_process"
        task.doing_task = now
        task.id_mercenary = current_user.id

        db.session.commit()
        flash(f"Вы успешно приняли задание и можете следить за его выполнением в вашем личном кабинете. Теперь вам нужно в течение 7 дней выполнить его, иначе оно исчезнет из вашего личного кабинета, а ваш статус заменится на проигравшего, что равносильно поражению в нашем виртуальном мире. Удачи вам с выполнением задания! ", "success")
    else:
        flash(f"Вы не являетесь наёмником, который может брать и выполнять задания", "danger")



    return redirect(request.referrer)

# task_details - модальное окно встроено и описано в самих HTML-шаблонах.


# task_download - функция, скачивающая задание в формате txt на компьютер пользователя
@app.route('/task_download/<int:id_task>/')
def task_download(id_task):

    task = Task.query.filter_by(id_task=id_task).first()
    content = f"""    
id задания #{task.id_task}
Название: {task.id_name_task}
Статус задания: {task.status_task}
Дата создания: {task.start_of_task}    
Цель задания: {task.purpose_task}
Место выполнения задания: {task.place_task}
Краткое описание: {task.short_description}
Полное описание: {task.full_description}
Организация: {task.fraction}
Рейтинг задания: {task.rating_task}
Награда за задание: {task.reward_task} 
"""
    
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=task_{task.fraction}_{task.id_task}.txt'
    return response

# <!-- rating.html - Страница, на которой отображены все наёмники и их рейтинг -->
@app.route('/rating/')
def rating():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    page = request.args.get('page', 1, type=int)
    
    pagination = (Mercenary.query.filter_by(status_mercenary="Alive").order_by(Mercenary.rating_mercenary.desc()).paginate(
        page=page,
        per_page=5,
        error_out=False)   
    )

    mercenaries = pagination.items

    completed_tasks=Task.query.filter_by(status_task="Done").all()


    return render_template('main_pages/rating.html', user_role=user_role, completed_tasks=completed_tasks, mercenaries=mercenaries, pagination=pagination)

# <!-- Механизмы rating -->



# <!-- Личные страницы пользователей -->

# <!-- admin.html - Страница инструментов администратора -->
@app.route('/admin/')
@check_rights(["admin"])
def admin():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    return render_template('user_pages/admin.html', user_role=user_role)

# <!-- member.html - Страница инструментов представителя -->
@app.route('/member/')
@check_rights(["member"])
def member():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    active_tasks = Task.query.filter_by( # Активные задания
    status_task="Active",
    fraction=current_user.member.fraction
    ).all()


    taken_tasks = Task.query.filter_by( # Взятые задания
    status_task="in_process",
    fraction=current_user.member.fraction
    ).all()

    active_reports = (Report.query
    .join(Report.task)
    .filter(Task.fraction == current_user.member.fraction,
            Report.status_report == "Active")
    .all())

    checked_reports = (Report.query
    .join(Report.task)
    .filter(Task.fraction == current_user.member.fraction,
            Report.status_report.in_(['Done', 'Rejected']))
    .all())

    report=Report.query.filter_by(
    id_mercenary=current_user.id,
    status_report="Active",
    ).all()



    return render_template('user_pages/member.html', user_role=user_role, 
    active_tasks=active_tasks, taken_tasks=taken_tasks, active_reports=active_reports, checked_reports=checked_reports)

# <!-- mercenary.html - Страница с личным кабинетом наёмника -->
@app.route('/mercenary/')
@check_rights(["mercenary"])
def mercenary():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    mercenary_tasks = Task.query.filter_by(id_mercenary=current_user.id, status_task="in_process").all() # Активные задания


    completed_tasks=Task.query.filter_by(id_mercenary=current_user.id, status_task="Done").all()

    report=Report.query.filter_by(
    id_mercenary=current_user.id,
    status_report="Active",
    ).all()

    return render_template('user_pages/mercenary.html', user_role=user_role, 
    report=report, mercenary_tasks=mercenary_tasks, completed_tasks=completed_tasks)



# <!-- Подстраницы с различными функциями для основных страниц пользователей -->

# Сохраняет список изображений (в формате base64) на диск.
# Возвращает строку с путями через запятую (относительно папки static),
# которую потом пишем в Report.path_image_report.
def save_report_images(base64_list, id_report):
    saved_paths = []
    for index, base64_string in enumerate(base64_list):
        # Отделяем метаданные "data:image/...;base64," от самих данных
        if 'base64,' in base64_string:
            image_data = base64_string.split('base64,')[-1]
        else:
            image_data = base64_string

        try:
            img_binary = base64.b64decode(image_data)
        except Exception as e:
            print(f"Ошибка декодирования Base64: {e}")
            continue

        # Уникальное имя: id отчёта + порядковый номер фото
        filename = f"report_{id_report}_{index}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, 'wb') as f:
            f.write(img_binary)

        # Путь относительно static -> удобно отдавать через url_for('static', ...)
        saved_paths.append(f"uploads/{filename}")

    # Все пути одной строкой через запятую
    return ",".join(saved_paths)


# <!-- create_record.html - Страница создания отчёта для задания -->
@app.route('/create_record/<int:id_task>', methods=['GET', 'POST'])
@check_rights(["mercenary"])
def create_record(id_task):
    task = Task.query.filter_by(id_task=id_task).first()

    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    if request.method == 'POST':
        text_report = request.form.get('text_report')      # текст отчёта
        images_json = request.form.get('images_data')      # JSON-массив base64-строк из drop-zone

        # Разбираем JSON-массив с фотографиями (если фоток нет — пустой список)
        try:
            images_list = json.loads(images_json) if images_json else []
        except Exception:
            images_list = []

        now = datetime.now().date()

        # 1) Создаём отчёт, чтобы получить его id (нужен для имён файлов)
        new_report = Report(
            id_task=id_task,
            id_mercenary=current_user.id,
            date_report=now,
            text_report=text_report,
            path_image_report=None,
            status_report="Active",
        )
        db.session.add(new_report)
        db.session.flush()  # БД присваивает id_report, транзакция ещё открыта

        # 2) Сохраняем картинки на диск и пишем пути в отчёт
        new_report.path_image_report = save_report_images(images_list, new_report.id_report)

        db.session.commit()

        flash("Отчёт успешно отправлен", "success")
        return redirect(url_for('mercenary'))

    return render_template('sub_user_pages/create_record.html', user_role=user_role, task=task)


# <!-- Просмотр отчётов по заданию: механизм, который отдаёт скинутые фотографии -->
@app.route('/report_view/<int:id_report>/<string:status_report>')
@check_rights(["member", "mercenary"])
def report_view(id_report, status_report):
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    report = Report.query.filter_by(id_report=id_report).first()
    task = Task.query.filter_by(id_task=report.id_task).first()

    reports = Report.query.filter_by(id_report=id_report).all()
    # Для каждого отчёта превращаем строку путей "uploads/a.jpg,uploads/b.jpg"
    # в список путей, чтобы шаблон мог пройтись по ним циклом и показать <img>.
    for report in reports:
        if report.path_image_report:
            report.images = report.path_image_report.split(",")
        else:
            report.images = []

    return render_template('sub_user_pages/show_report.html', user_role=user_role, task=task, reports=reports, status_report=status_report)

# Принять отчёт - наёмнику засчитывается задания и оно считается выполненным и наёмнику начисляют рейтинг
@app.route('/report_accept/<int:id_report>')
@check_rights(["member"])
def report_accept(id_report):

    now = datetime.now().date()
    
    report = Report.query.filter_by(id_report=id_report).first()

    mercenary = (User.query
          .join(Mercenary, User.id == Mercenary.id_mercenary)
          .filter(User.id == report.id_mercenary)
          .first()) # Поставляем данные нужного пользователя по его id
    
    task = Task.query.filter_by(id_task=report.id_task).first() # Задание, к которому относится отчёт
    
    reports_in_special_task = Report.query.filter(report.id_task == task.id_task, mercenary.mercenary.id_mercenary == report.id_mercenary).all()

    # Изменения в данных

    for rep in reports_in_special_task: # Изменяем статус всех отчётов на то, что они проверены.
        rep.status_report = "Done"

    mercenary_did_task = Task.query.filter_by(id_mercenary=task.id_mercenary, status_task="Done").all()
    #Изменения в данных
    task.status_task = "Done"
    task.end_of_task = now

    db.session.commit() #Засчитали всю часть, связанную с заданиями

    all_price_mercenary = 0 # Все деньги, которые наёмник получил за все миссии

    for t in mercenary_did_task:
        all_price_mercenary = all_price_mercenary + t.reward_task

    mercenary_favourite_fraction = (db.session.query(Task.fraction, func.count(Task.fraction))
        .filter_by(id_mercenary=task.id_mercenary, status_task="Done")
        .group_by(Task.fraction)
        .order_by(func.count(Task.fraction).desc(), func.sum(Task.reward_task).desc())
        .first())

    mercenary.mercenary.rating_mercenary = mercenary.mercenary.rating_mercenary + task.rating_task # Увеличиваем рейтинг наёмника

    mercenary.mercenary.favourite_fraction = mercenary_favourite_fraction[0]

    mercenary.mercenary.price_mercenary = all_price_mercenary // len(mercenary_did_task)

    mercenary.mercenary.status_mercenary = "Alive"

    db.session.commit()

    flash("Отчёт засчитан, задание считается выполненным " \
    "и наёмнику добавлен новый рейтинг. " \
    "В связи с этим свяжитесь с наёмником " \
    "и переведите ему положенную сумму игровой валюты.", 
    "success")

    return redirect(request.referrer)

# Отклонить отчёт - отчёт отклоняется и задание не считается выполненным. Представителю отображается предупреждение
@app.route('/report_cancel/<int:id_report>')
@check_rights(["member"])
def report_cancel(id_report):

    report=Report.query.filter_by(id_report=id_report).first()

    report.status_report = "Rejected"

    db.session.commit()

    flash("Отчёт не засчитан и задание не считается выполненным. " \
    "Будьте осторожны, если наёмник добросовестно выполнил задание, " \
    "а вы его не зачли, то он может рассердиться, " \
    "порвать связи с вашей организацией " \
    "и начать работать уже на ваших конкурентов, " \
    "что принесёт вам только убытки. ", 
    "danger")

    return redirect(request.referrer)


# <!-- create_task.html - Страница создания задания -->
@app.route('/create_task/', methods=['GET', 'POST'])
@check_rights(["member", "admin"])
def create_task():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    if request.method == 'POST':

        id_name_task = request.form.get('name_task')
        short_description = request.form.get('short_description')
        full_description = request.form.get('full_description')
        purpose_task = request.form.get('purpose_task')
        place_task = request.form.get('place_task')
        rating_task = request.form.get('rating_task')
        reward_task = request.form.get('reward_task')

        if (current_user.role == "admin"):
            fraction = request.form.get('fraction')
        elif (current_user.role == "member"):
            fraction = current_user.member.fraction

        userdata = Task.query.filter_by(id_name_task=id_name_task).first()
        now = datetime.now().date() # Дата регистрации

        if (not userdata):
            try:
                new_task = Task( # Создаём новую запись в таблице User
                    id_name_task = id_name_task, 
                    short_description = short_description, 
                    full_description = full_description,
                    purpose_task = purpose_task,
                    place_task = place_task,
                    rating_task = rating_task,
                    reward_task = reward_task,
                    fraction = fraction,

                    id_mercenary = None,
                    status_task = "Active",

                    start_of_task = now,
                    doing_task = None,
                    end_of_task = None,
                )

                db.session.add(new_task)
                db.session.commit()   

                flash("Вы успешно создали новое задание", "success")
                return redirect(url_for('main_page'))
            except Exception as e:
                flash("Ошибка:" + str(e), "danger")

        else:
            flash(f"Вы неправильно ввели данные, попробуйте ещё раз", "danger")
            return redirect(url_for('create_task'))


    return render_template('sub_user_pages/create_task.html', user_role=user_role)



# <!-- Страницы администраторов с таблицами по управлению объектами в системе -->

# <!-- CRUD-таблицы -->

# <!-- CRUD_table_member.html - Страница с таблицей с CRUD-функциями всех записей представителей -->
@app.route('/CRUD_table_member/')
@check_rights(["admin"])
def CRUD_table_member():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    
    members = User.query.join(Member, User.id == Member.id_member).all()
    return render_template('admin_tables/CRUD_table_member.html', user_role=user_role, members=members)

# <!-- CRUD_table_mercenary.html - Страница с таблицей с CRUD-функциями всех записей наёмников -->
@app.route('/CRUD_table_mercenary/')
@check_rights(["admin"])
def CRUD_table_mercenary():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    mercenaries = User.query.join(Mercenary, User.id == Mercenary.id_mercenary).all()

    return render_template('admin_tables/CRUD_table_mercenary.html', user_role=user_role, mercenaries=mercenaries)

# <!-- CRUD_table_task.html - Страница с таблицей с CRUD-функциями всех заданий -->
@app.route('/CRUD_table_task/')
@check_rights(["admin"])
def CRUD_table_task():
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    tasks = Task.query.all()

    return render_template('admin_tables/CRUD_table_task.html', user_role=user_role, tasks=tasks)



# <!-- READ таблицы -->

# <!-- READ_table_member.html - Страница с таблицей для READ-UPDATE всех записей представителей -->
@app.route('/READ_table_member/<int:id>', methods=['GET', 'POST'])
@check_rights(["admin"])
def READ_table_member(id):
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    
    member = (User.query
          .join(Member, User.id == Member.id_member)
          .filter(User.id == id)
          .first()) #Поставляем данные нужного пользователя по его id

    return render_template('admin_tables/READ_table_member.html', user_role=user_role, member=member)

# <!-- READ_table_mercenary.html - Страница с таблицей для READ-UPDATE всех записей наёмников -->
@app.route('/READ_table_mercenary/<int:id>', methods=['GET', 'POST'])
@check_rights(["admin"])
def READ_table_mercenary(id):
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    mercenary = (User.query
          .join(Mercenary, User.id == Mercenary.id_mercenary)
          .filter(User.id == id)
          .first()) #Поставляем данные нужного пользователя по его id

    return render_template('admin_tables/READ_table_mercenary.html', user_role=user_role, mercenary=mercenary)

# <!-- READ_table_task.html - Страница с таблицей для READ-UPDATE всех заданий -->
@app.route('/READ_table_task/<int:id_task>', methods=['GET', 'POST'])
@check_rights(["admin"])
def READ_table_task(id_task):
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    task = Task.query.filter_by(id_task=id_task).first()
    return render_template('admin_tables/READ_table_task.html', user_role=user_role, task=task)



# <!-- UPDATE таблицы -->

# <!-- UPDATE_table_member.html - Страница с таблицей для READ-UPDATE всех записей представителей -->
@app.route('/UPDATE_table_member/<int:id>', methods=['GET', 'POST'])
@check_rights(["admin"])
def UPDATE_table_member(id):
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    member = (User.query
          .join(Member, User.id == Member.id_member)
          .filter(User.id == id)
          .first()) #Поставляем данные нужного пользователя по его id
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        fraction = request.form.get('fraction')
        fraction_code = request.form.get('fraction_code')

        member.username = username
        member.password = password
        member.member.fraction = fraction
        member.member.fraction_code = fraction_code
        db.session.commit()
        flash(f"Изменения успешно применены", "success")

        member = (User.query
          .join(Member, User.id == Member.id_member)
          .filter(User.id == id)
          .first()) #Поставляем данные нужного пользователя по его id
        return render_template('admin_tables/UPDATE_table_member.html', user_role=user_role, member=member)

    return render_template('admin_tables/UPDATE_table_member.html', user_role=user_role, member=member)




# <!-- UPDATE_table_mercenary.html - Страница с таблицей для READ-UPDATE всех записей наёмников -->
@app.route('/UPDATE_table_mercenary/<int:id>', methods=['GET', 'POST'])
@check_rights(["admin"])
def UPDATE_table_mercenary(id):
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался

    mercenary = (User.query
          .join(Mercenary, User.id == Mercenary.id_mercenary)
          .filter(User.id == id)
          .first()) #Поставляем данные нужного пользователя по его id
    
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        telegram_username = request.form.get('telegram_username')
        rating_mercenary = request.form.get('rating_mercenary')
        status_mercenary = request.form.get('status_mercenary')
        favourite_fraction = request.form.get('favourite_fraction')
        price_mercenary = request.form.get('price_mercenary')

        mercenary.username = username
        mercenary.password = password
        mercenary.mercenary.telegram_username = telegram_username
        mercenary.mercenary.rating_mercenary = rating_mercenary
        mercenary.mercenary.status_mercenary = status_mercenary
        mercenary.mercenary.favourite_fraction = favourite_fraction
        mercenary.mercenary.price_mercenary = price_mercenary

        db.session.commit()
        flash(f"Изменения успешно применены", "success")

        mercenary = (User.query
          .join(Mercenary, User.id == Mercenary.id_mercenary)
          .filter(User.id == id)
          .first()) #Поставляем данные нужного пользователя по его id
        
        return render_template('admin_tables/UPDATE_table_mercenary.html', user_role=user_role, mercenary=mercenary)

    return render_template('admin_tables/UPDATE_table_mercenary.html', user_role=user_role, mercenary=mercenary)

# <!-- UPDATE_table_task.html - Страница с таблицей для READ-UPDATE всех заданий -->
@app.route('/UPDATE_table_task/<int:id_task>', methods=['GET', 'POST'])
@check_rights(["admin"])
def UPDATE_table_task(id_task):
    user_role = auth() # Функция, которая отображает роль, если пользователь регистрировался или не регистрировался
    
    task = Task.query.filter_by(id_task=id_task).first()
    
    if request.method == 'POST':

        id_name_task = request.form.get('id_name_task')
        short_description = request.form.get('short_description')
        full_description = request.form.get('full_description')
        purpose_task = request.form.get('purpose_task')
        place_task = request.form.get('place_task')
        rating_task = request.form.get('rating_task')
        reward_task = request.form.get('reward_task')
        fraction = request.form.get('fraction')


        task.id_name_task = id_name_task
        task.short_description = short_description
        task.full_description = full_description
        task.purpose_task = purpose_task
        task.place_task = place_task
        task.rating_task = rating_task
        task.reward_task = reward_task
        task.fraction = fraction

        db.session.commit()
        flash(f"Изменения успешно применены", "success")

        task = Task.query.filter_by(id_task=id_task).first()
        
        return render_template('admin_tables/UPDATE_table_task.html', user_role=user_role, task=task)

    return render_template('admin_tables/UPDATE_table_task.html', user_role=user_role, task=task)



# <!-- Удаление объектов -->

# <!-- Удаление наёмника из системы -->
@app.route('/delete_mercenary/<int:id>', methods=['GET', 'POST'])
@check_rights(["admin"])
def delete_mercenary(id):
    user = User.query.get(id)
    
    db.session.delete(user)
    db.session.commit()

    flash("Запись наёмника удалена", "success")
    return redirect(request.referrer)

# <!-- Удаление представителя из системы -->
@app.route('/delete_member/<int:id>', methods=['GET', 'POST'])
@check_rights(["admin"])
def delete_member(id):
    user = User.query.get(id)
    
    db.session.delete(user)
    db.session.commit()

    flash("Запись представителя удалена", "success")
    return redirect(request.referrer)

# <!-- Удаление задания из системы -->
@app.route('/delete_task/<int:id_task>', methods=['GET', 'POST'])
@check_rights(["admin"])
def delete_task(id_task):
    task = Task.query.get(id_task)
    
    db.session.delete(task)
    db.session.commit()

    flash("Задание удалено", "success")
    return redirect(request.referrer)









#<!-- Механизм реализации работы с загруженными картинками в отчётах -->

# Убедимся, что папка для загрузок существует
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def save_image_from_base64(base64_string, object_id):
    """
    Декодирует Base64 строку и сохраняет изображение на диске.
    Возвращает относительный путь к сохранённому файлу.
    """
    # Формат: "data:image/png;base64,<actual_base64_data>"
    # Нам нужно отделить метаданные от самих данных
    if 'base64,' in base64_string:
        # Берем часть после запятой
        image_data = base64_string.split('base64,')[-1]
    else:
        image_data = base64_string

    # Декодируем строку Base64 в бинарные данные
    try:
        img_binary = base64.b64decode(image_data)
    except Exception as e:
        print(f"Ошибка декодирования Base64: {e}")
        return None

    # Генерируем уникальное имя файла
    filename = f"object_{object_id}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Сохраняем файл
    with open(filepath, 'wb') as f:
        f.write(img_binary)

    # Возвращаем относительный путь для использования в HTML
    return os.path.join('static', 'uploads', filename)


@app.route('/object/<int:object_id>/upload_image', methods=['GET', 'POST'])
def save_object_image(object_id):
    """
    Обрабатывает загрузку изображения для объекта с ID = object_id.
    """
    if request.method == 'POST':
        # Получаем данные изображения из формы
        base64_image = request.form.get('image_data')

        if not base64_image:
            return "Ошибка: Нет данных изображения.", 400

        # Сохраняем изображение на диск
        image_path = save_image_from_base64(base64_image, object_id)

        if not image_path:
            return "Ошибка: Не удалось сохранить изображение.", 500

        # --- КЛЮЧЕВОЙ МОМЕНТ: Сохранение пути в объект БД ---
        # Здесь вы должны обновить запись вашего объекта в базе данных.
        # Пример (допустим, у вас есть модель Object):
        # from yourapp.models import Object, db
        # obj = Object.query.get(object_id)
        # obj.image_filename = image_path  # сохраняем путь
        # db.session.commit()

        print(f"Изображение для объекта {object_id} сохранено как {image_path}")

        # После успешного сохранения перенаправляем на страницу просмотра объекта
        # Этот маршрут должен показывать объект с уже привязанной картинкой
        return redirect(url_for('show_object', object_id=object_id))

    # Для GET-запроса просто показываем страницу загрузки
    return render_template('upload_image.html', object_id=object_id)



# <!-- Функция для просмотра созданного отчёта для задания -->
@app.route('/object/<int:object_id>')
def show_object(object_id):
    """
    Страница для просмотра объекта с его изображением.
    """
    # --- Получаем данные объекта из БД ---
    # Здесь вы должны получить объект из базы данных.
    # Пример:
    # obj = Object.query.get(object_id)
    # image_url = obj.image_filename or '/static/default.jpg'

    # Временные данные для примера
    image_url = url_for('static', filename=f'uploads/object_{object_id}.jpg')

    return f"""
    <h1>Просмотр объекта #{object_id}</h1>
    <img src="{image_url}" alt="Изображение объекта" style="max-width: 400px;">
    <br><br>
    <a href="{url_for('save_object_image', object_id=object_id)}">Загрузить новое изображение</a>
    """

if __name__ == "__main__":
    app.run(debug=True)


