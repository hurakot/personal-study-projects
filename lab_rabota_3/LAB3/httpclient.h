#ifndef HTTPCLIENT_H
#define HTTPCLIENT_H

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include "nerf.h"

class HttpClient : public QObject {
    Q_OBJECT
public:
    // === Singleton ===
    static HttpClient& instance();

    HttpClient(const HttpClient&) = delete;
    HttpClient& operator=(const HttpClient&) = delete;

    void setBaseUrl(const QString &url) { m_baseUrl = url; }

    // === Adapter: C++ методы -> REST вызовы ===
    void getAll();                       // GET    /api/nerf/
    void getById(int id);                // GET    /api/nerf/{id}/
    void create(const Nerf &nerf);       // POST   /api/nerf/
    void update(const Nerf &nerf);       // PUT    /api/nerf/{id}/
    void remove(int id);                 // DELETE /api/nerf/{id}/

signals:
    void getAllFinished(const QList<Nerf> &items, const QString &raw);
    void getByIdFinished(const Nerf &item, const QString &raw);
    void createFinished(const Nerf &item, const QString &raw);
    void updateFinished(const Nerf &item, const QString &raw);
    void removeFinished(int id, const QString &raw);
    void errorOccurred(const QString &message);

private:
    explicit HttpClient(QObject *parent = nullptr);
    ~HttpClient() override = default;

    QNetworkAccessManager *m_manager;
    QString m_baseUrl;

    QNetworkRequest makeRequest(const QString &path) const;
    QString readReply(QNetworkReply *reply) const;
};

#endif