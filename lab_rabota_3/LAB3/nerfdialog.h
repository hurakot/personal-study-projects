#ifndef NERFDIALOG_H
#define NERFDIALOG_H

#include <QDialog>
#include "nerf.h"

QT_BEGIN_NAMESPACE
namespace Ui { class NerfDialog; }
QT_END_NAMESPACE

class NerfDialog : public QDialog {
    Q_OBJECT
public:
    enum class Mode { Create, Update };

    explicit NerfDialog(Mode mode, QWidget *parent = nullptr);
    ~NerfDialog();

    // Заполнить поля из существующего объекта (для режима Update)
    void setNerf(const Nerf &n);

    // Собрать объект из полей
    Nerf nerf() const;

private:
    Ui::NerfDialog *ui;
    Mode m_mode;
    int  m_id = 0;   // используется в режиме Update
};

#endif