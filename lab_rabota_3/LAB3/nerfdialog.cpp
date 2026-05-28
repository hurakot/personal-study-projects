#include "nerfdialog.h"
#include "ui_nerfdialog.h"

NerfDialog::NerfDialog(Mode mode, QWidget *parent)
    : QDialog(parent),
    ui(new Ui::NerfDialog),
    m_mode(mode)
{
    ui->setupUi(this);

    setWindowTitle(mode == Mode::Create
                       ? "Создать Nerf"
                       : "Обновить Nerf");

    // Разумные дефолтные значения для нового объекта
    ui->spinPrice->setRange(0.0, 1000000.0);
    ui->spinPrice->setDecimals(2);
    ui->spinPrice->setValue(0.0);

    ui->dateTimeCreate->setDate(QDate::currentDate());
    ui->dateTimeCreate->setDisplayFormat("yyyy-MM-dd");

    ui->checkAvailable->setChecked(true);
}

NerfDialog::~NerfDialog() {
    delete ui;
}

void NerfDialog::setNerf(const Nerf &n) {
    m_id = n.id();
    ui->editTitle->setText(n.title());
    ui->editSeries->setText(n.series());
    ui->editBullet->setText(n.bullet());
    ui->spinPrice->setValue(n.price());

    // time_create приходит как "yyyy-MM-dd"
    QDate d = QDate::fromString(n.timeCreate(), "yyyy-MM-dd");
    if (d.isValid())
        ui->dateTimeCreate->setDate(d);

    ui->checkAvailable->setChecked(n.available());
}

Nerf NerfDialog::nerf() const {
    Nerf n;
    n.setId(m_id);   // 0 в режиме Create, реальный id в режиме Update
    n.setTitle(ui->editTitle->text());
    n.setSeries(ui->editSeries->text());
    n.setBullet(ui->editBullet->text());
    n.setPrice(ui->spinPrice->value());
    n.setTimeCreate(ui->dateTimeCreate->date().toString("yyyy-MM-dd"));
    n.setAvailable(ui->checkAvailable->isChecked());
    return n;
}