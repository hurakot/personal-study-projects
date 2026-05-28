#ifndef NERF_H
#define NERF_H

#include <QString>
#include <QJsonObject>

class Nerf {
public:
    Nerf() = default;
    Nerf(int id,
         const QString &title,
         const QString &series,
         const QString &bullet,
         double price,
         const QString &timeCreate,
         bool available);

    int id() const { return m_id; }
    QString title() const { return m_title; }
    QString series() const { return m_series; }
    QString bullet() const { return m_bullet; }
    double  price() const { return m_price; }
    QString timeCreate() const { return m_timeCreate; }
    QString createdAt() const { return m_createdAt; }
    bool    available() const { return m_available; }

    void setId(int id) { m_id = id; }
    void setTitle(const QString &v) { m_title = v; }
    void setSeries(const QString &v) { m_series = v; }
    void setBullet(const QString &v) { m_bullet = v; }
    void setPrice(double v) { m_price = v; }
    void setTimeCreate(const QString &v) { m_timeCreate = v; }
    void setAvailable(bool v) { m_available = v; }

    // Сериализация / десериализация — основа адаптера C++ <-> JSON
    QJsonObject toJson() const;
    static Nerf fromJson(const QJsonObject &obj);

    QString toString() const;

private:
    int     m_id = 0;
    QString m_title;
    QString m_series;
    QString m_bullet;
    double  m_price = 0.0;
    QString m_timeCreate;   // дата выпуска, YYYY-MM-DD
    QString m_createdAt;    // readonly, заполняется сервером
    bool    m_available = true;
};

#endif