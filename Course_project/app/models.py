from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ---------- Базовая таблица пользователей ----------
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    registration_date = db.Column(db.Date)

    # Связи 1:1 с ролями (#1-#6). uselist=False -> один объект, не список
    mercenary = db.relationship("Mercenary", back_populates="user", uselist=False, cascade="all, delete-orphan",)
    member = db.relationship("Member", back_populates="user", uselist=False, cascade="all, delete-orphan",)
    administrator = db.relationship("Administrator", back_populates="user", uselist=False, cascade="all, delete-orphan",)

    # Роль определяется тем, в какой таблице-роли есть запись с этим user.id
    @property
    def role(self):
        if self.administrator:
            return "admin"
        if self.member:
            return "member"
        if self.mercenary:
            return "mercenary"
        return None


# ---------- Роли: PK = FK на users.id -> гарантированно 1:1 (#1-#6) ----------
class Administrator(db.Model):
    __tablename__ = "administrators"
    id_administrator = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)

    user = db.relationship("User", back_populates="administrator")


class Member(db.Model):
    __tablename__ = "members"
    id_member = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    fraction = db.Column(db.Text)
    fraction_code = db.Column(db.Text)

    user = db.relationship("User", back_populates="member")


class Mercenary(db.Model):
    __tablename__ = "mercenaries"
    id_mercenary = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    telegram_username = db.Column(db.Text)
    # #8: FK на УНИКАЛЬНУЮ колонку certificate_code в таблице сертификатов
    certificate_code = db.Column(db.Text, db.ForeignKey("certificates.certificate_code")) # Код сертификата - текст
    rating_mercenary = db.Column(db.Integer)
    status_mercenary = db.Column(db.Text)
    favourite_fraction = db.Column(db.Text)
    price_mercenary = db.Column(db.Float)

    user = db.relationship("User", back_populates="mercenary")
    certificate = db.relationship("Certificate", back_populates="mercenary", uselist=False)  # #8

    # 1:N (#12): один наёмник -> много заданий
    tasks = db.relationship("Task", back_populates="executor")
    # 1:N (#9, реализовано как 1:N): один наёмник -> много отчётов
    reports = db.relationship("Report", back_populates="mercenary")


# ---------- Сертификаты ----------
class Certificate(db.Model):
    __tablename__ = "certificates"
    id_certificate = db.Column(db.Integer, primary_key=True)
    # должен быть unique, иначе FK из mercenaries на него не сработает
    certificate_code = db.Column(db.Text, unique=True) # Код сертификата - текст
    registration_date_certificate = db.Column(db.Date)
    place_certification = db.Column(db.Text, default="Новый Карфаген")
    giving_certificate = db.Column(db.Text, default="Единорог")

    mercenary = db.relationship("Mercenary", back_populates="certificate", uselist=False)


# ---------- Задания ----------
class Task(db.Model):
    __tablename__ = "tasks"
    id_task = db.Column(db.Integer, primary_key=True)
    id_name_task = db.Column(db.Text, unique=True)
    short_description = db.Column(db.Text)
    full_description = db.Column(db.Text)
    purpose_task = db.Column(db.Text)
    place_task = db.Column(db.Text)
    rating_task = db.Column(db.Integer)
    reward_task = db.Column(db.Float)
    fraction = db.Column(db.Text)
    # FK на исполнителя (#12)
    id_mercenary = db.Column(db.Integer, db.ForeignKey("mercenaries.id_mercenary"))
    status_task = db.Column(db.Text)
    start_of_task = db.Column(db.Date)
    doing_task = db.Column(db.Date)
    end_of_task = db.Column(db.Date)

    executor = db.relationship("Mercenary", back_populates="tasks")          # #12
    # 1:N (#11): одно задание -> много отчётов
    reports = db.relationship("Report", back_populates="task",
                              cascade="all, delete-orphan")


# ---------- Отчёты ----------
class Report(db.Model):
    __tablename__ = "reports"
    id_report = db.Column(db.Integer, primary_key=True)
    id_task = db.Column(db.Integer, db.ForeignKey("tasks.id_task"))           # #11
    status_report = db.Column(db.Text) # Статус отчёта "Active" - "непроверен", "Done" - проверен, "Rejected" - отвергнут
    id_mercenary = db.Column(db.Integer, db.ForeignKey("mercenaries.id_mercenary"))  # #9
    date_report = db.Column(db.Date)
    text_report = db.Column(db.Text)
    path_image_report = db.Column(db.Text)

    task = db.relationship("Task", back_populates="reports")                  # #11
    mercenary = db.relationship("Mercenary", back_populates="reports")
    
