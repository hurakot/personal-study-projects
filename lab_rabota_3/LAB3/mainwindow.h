#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "nerf.h"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void onGetAllClicked();
    void onGetByIdClicked();
    void onCreateClicked();
    void onUpdateClicked();
    void onDeleteClicked();

    void handleGetAll(const QList<Nerf> &items, const QString &raw);
    void handleGetById(const Nerf &item, const QString &raw);
    void handleCreate(const Nerf &item, const QString &raw);
    void handleUpdate(const Nerf &item, const QString &raw);
    void handleRemove(int id, const QString &raw);
    void handleError(const QString &msg);

private:
    Ui::MainWindow *ui;
};

#endif
