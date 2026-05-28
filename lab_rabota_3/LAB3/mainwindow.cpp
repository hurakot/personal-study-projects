#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "nerfdialog.h"
#include "httpclient.h"
#include <QDebug>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    HttpClient::instance().setBaseUrl("http://127.0.0.1:8000");

    connect(ui->btnModeLocal, &QPushButton::clicked, this, [this]() {
        HttpClient::instance().setBaseUrl("http://127.0.0.1:8000");
        ui->txtOutput->append("== Локальный режим");
    });

    connect(ui->btnModeDocker, &QPushButton::clicked, this, [this]() {
        HttpClient::instance().setBaseUrl("https://localhost");
        ui->txtOutput->append("== Docker режим");
    });

    connect(ui->btnGetAll,  &QPushButton::clicked, this, &MainWindow::onGetAllClicked);
    connect(ui->btnGetById, &QPushButton::clicked, this, &MainWindow::onGetByIdClicked);
    connect(ui->btnCreate,  &QPushButton::clicked, this, &MainWindow::onCreateClicked);
    connect(ui->btnUpdate,  &QPushButton::clicked, this, &MainWindow::onUpdateClicked);
    connect(ui->btnDelete,  &QPushButton::clicked, this, &MainWindow::onDeleteClicked);

    auto &client = HttpClient::instance();
    connect(&client, &HttpClient::getAllFinished,  this, &MainWindow::handleGetAll);
    connect(&client, &HttpClient::getByIdFinished, this, &MainWindow::handleGetById);
    connect(&client, &HttpClient::createFinished,  this, &MainWindow::handleCreate);
    connect(&client, &HttpClient::updateFinished,  this, &MainWindow::handleUpdate);
    connect(&client, &HttpClient::removeFinished,  this, &MainWindow::handleRemove);
    connect(&client, &HttpClient::errorOccurred,   this, &MainWindow::handleError);
}

MainWindow::~MainWindow() { delete ui; }

void MainWindow::onGetAllClicked() {
    ui->txtOutput->append(">> GET ALL");
    HttpClient::instance().getAll();
}

void MainWindow::onGetByIdClicked() {
    int id = ui->editId->text().toInt();
    ui->txtOutput->append(QString(">> GET id=%1").arg(id));
    HttpClient::instance().getById(id);
}

void MainWindow::onCreateClicked() {
    NerfDialog dlg(NerfDialog::Mode::Create, this);
    if (dlg.exec() != QDialog::Accepted)
        return;

    Nerf n = dlg.nerf();
    ui->txtOutput->append(">> CREATE: " + n.toString());
    HttpClient::instance().create(n);
}

void MainWindow::onUpdateClicked() {
    int id = ui->editId->text().toInt();
    if (id <= 0) {
        ui->txtOutput->append("!! Укажите валидный ID для Update");
        return;
    }

    // Сначала получаем актуальные данные с сервера, чтобы заполнить форму.
    // Это асинхронно: показываем диалог в обработчике сигнала getByIdFinished.
    auto &client = HttpClient::instance();

    // Одноразовое подключение: получили данные, открыли диалог, отписались.
    auto *conn = new QMetaObject::Connection;
    *conn = connect(&client, &HttpClient::getByIdFinished, this,
                    [this, conn](const Nerf &item, const QString &) {
                        QObject::disconnect(*conn);
                        delete conn;

                        NerfDialog dlg(NerfDialog::Mode::Update, this);
                        dlg.setNerf(item);
                        if (dlg.exec() != QDialog::Accepted)
                            return;

                        Nerf updated = dlg.nerf();
                        ui->txtOutput->append(">> UPDATE: " + updated.toString());
                        HttpClient::instance().update(updated);
                    });

    ui->txtOutput->append(QString(">> Запрашиваем данные id=%1 для редактирования…").arg(id));
    client.getById(id);
}

void MainWindow::onDeleteClicked() {
    int id = ui->editId->text().toInt();
    ui->txtOutput->append(QString(">> DELETE id=%1").arg(id));
    HttpClient::instance().remove(id);
}

void MainWindow::handleGetAll(const QList<Nerf> &items, const QString &raw) {
    qDebug() << "GET ALL raw:" << raw;
    ui->txtOutput->append(QString("<< GET %1 records:").arg(items.size()));
    for (const auto &n : items) {
        qDebug() << n.toString();
        ui->txtOutput->append("  " + n.toString());
    }
}

void MainWindow::handleGetById(const Nerf &item, const QString &raw) {
    qDebug() << "GET BY ID raw:" << raw;
    qDebug() << item.toString();
    ui->txtOutput->append("<< " + item.toString());
}

void MainWindow::handleCreate(const Nerf &item, const QString &raw) {
    qDebug() << "CREATE raw:" << raw;
    ui->txtOutput->append("<< CREATED: " + item.toString());
}

void MainWindow::handleUpdate(const Nerf &item, const QString &raw) {
    qDebug() << "UPDATE raw:" << raw;
    ui->txtOutput->append("<< UPDATED: " + item.toString());
}

void MainWindow::handleRemove(int id, const QString &raw) {
    qDebug() << "DELETE raw:" << raw;
    ui->txtOutput->append(QString("<< DELEED record id=%1").arg(id));
}

void MainWindow::handleError(const QString &msg) {
    qDebug() << "ERROR:" << msg;
    ui->txtOutput->append("!! ERROR: " + msg);
}
