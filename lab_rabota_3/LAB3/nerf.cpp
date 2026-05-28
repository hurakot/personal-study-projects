#include "nerf.h"

Nerf::Nerf(int id,
           const QString &title,
           const QString &series,
           const QString &bullet,
           double price,
           const QString &timeCreate,
           bool available)
    : m_id(id),
    m_title(title),
    m_series(series),
    m_bullet(bullet),
    m_price(price),
    m_timeCreate(timeCreate),
    m_available(available) {}

QJsonObject Nerf::toJson() const {
    QJsonObject obj;
    // id и created_at не отправляем — сервер ими управляет
    obj["title"]       = m_title;
    obj["series"]      = m_series;
    obj["bullet"]      = m_bullet;
    obj["price"]       = m_price;
    obj["time_create"] = m_timeCreate;
    obj["available"]   = m_available;
    return obj;
}

Nerf Nerf::fromJson(const QJsonObject &obj) {
    Nerf n;
    n.m_id         = obj.value("id").toInt();
    n.m_title      = obj.value("title").toString();
    n.m_series     = obj.value("series").toString();
    n.m_bullet     = obj.value("bullet").toString();
    n.m_price      = obj.value("price").toDouble();
    n.m_timeCreate = obj.value("time_create").toString();
    n.m_createdAt  = obj.value("created_at").toString();
    n.m_available  = obj.value("available").toBool();
    return n;
}

QString Nerf::toString() const {
    return QString("Nerf{id=%1, title='%2', series='%3', bullet='%4', "
                   "price=%5, time_create=%6, available=%7}")
        .arg(m_id)
        .arg(m_title, m_series, m_bullet)
        .arg(m_price)
        .arg(m_timeCreate)
        .arg(m_available ? "true" : "false");
}