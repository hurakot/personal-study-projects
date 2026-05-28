#include "httpclient.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <QUrl>
#include <QDebug>
#include <QSslError>

HttpClient& HttpClient::instance() {
    static HttpClient inst;
    return inst;
}

HttpClient::HttpClient(QObject *parent)
    : QObject(parent),
    m_manager(new QNetworkAccessManager(this)),
    m_baseUrl("http://127.0.0.1:8000")
{}

QNetworkRequest HttpClient::makeRequest(const QString &path) const {
    QNetworkRequest req(QUrl(m_baseUrl + path));
    req.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    return req;
}

QString HttpClient::readReply(QNetworkReply *reply) const {
    return QString::fromUtf8(reply->readAll());
}

// ---------- GET ALL ----------
void HttpClient::getAll() {
    QNetworkReply *reply = m_manager->get(makeRequest("/api/nerf/"));

    connect(reply, &QNetworkReply::sslErrors, reply,
            [reply](const QList<QSslError> &errors) {
                Q_UNUSED(errors);
                reply->ignoreSslErrors();
            });

    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        QString raw = readReply(reply);
        if (reply->error() != QNetworkReply::NoError) {
            emit errorOccurred(reply->errorString() + "\n" + raw);
        } else {
            QList<Nerf> items;
            auto doc = QJsonDocument::fromJson(raw.toUtf8());
            if (doc.isArray()) {
                for (const auto &v : doc.array())
                    items.append(Nerf::fromJson(v.toObject()));
            } else if (doc.isObject() && doc.object().contains("results")) {
                for (const auto &v : doc.object().value("results").toArray())
                    items.append(Nerf::fromJson(v.toObject()));
            }
            emit getAllFinished(items, raw);
        }
        reply->deleteLater();
    });
}

// ---------- GET BY ID ----------
void HttpClient::getById(int id) {
    QNetworkReply *reply = m_manager->get(
        makeRequest(QString("/api/nerf/%1/").arg(id)));

    connect(reply, &QNetworkReply::sslErrors, reply,
            [reply](const QList<QSslError> &errors) {
                Q_UNUSED(errors);
                reply->ignoreSslErrors();
            });

    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        QString raw = readReply(reply);
        if (reply->error() != QNetworkReply::NoError) {
            emit errorOccurred(reply->errorString() + "\n" + raw);
        } else {
            Nerf n = Nerf::fromJson(QJsonDocument::fromJson(raw.toUtf8()).object());
            emit getByIdFinished(n, raw);
        }
        reply->deleteLater();
    });
}

// ---------- CREATE (POST) ----------
void HttpClient::create(const Nerf &nerf) {
    QByteArray payload = QJsonDocument(nerf.toJson()).toJson();
    QNetworkReply *reply = m_manager->post(makeRequest("/api/nerf/"), payload);

    connect(reply, &QNetworkReply::sslErrors, reply,
            [reply](const QList<QSslError> &errors) {
                Q_UNUSED(errors);
                reply->ignoreSslErrors();
            });

    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        QString raw = readReply(reply);
        if (reply->error() != QNetworkReply::NoError) {
            emit errorOccurred(reply->errorString() + "\n" + raw);
        } else {
            Nerf n = Nerf::fromJson(QJsonDocument::fromJson(raw.toUtf8()).object());
            emit createFinished(n, raw);
        }
        reply->deleteLater();
    });
}

// ---------- UPDATE (PUT) ----------
void HttpClient::update(const Nerf &nerf) {
    QByteArray payload = QJsonDocument(nerf.toJson()).toJson();
    QNetworkReply *reply = m_manager->put(
        makeRequest(QString("/api/nerf/%1/").arg(nerf.id())), payload);

    connect(reply, &QNetworkReply::sslErrors, reply,
            [reply](const QList<QSslError> &errors) {
                Q_UNUSED(errors);
                reply->ignoreSslErrors();
            });

    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        QString raw = readReply(reply);
        if (reply->error() != QNetworkReply::NoError) {
            emit errorOccurred(reply->errorString() + "\n" + raw);
        } else {
            Nerf n = Nerf::fromJson(QJsonDocument::fromJson(raw.toUtf8()).object());
            emit updateFinished(n, raw);
        }
        reply->deleteLater();
    });
}

// ---------- DELETE ----------
void HttpClient::remove(int id) {
    QNetworkReply *reply = m_manager->deleteResource(
        makeRequest(QString("/api/nerf/%1/").arg(id)));

    connect(reply, &QNetworkReply::sslErrors, reply,
            [reply](const QList<QSslError> &errors) {
                Q_UNUSED(errors);
                reply->ignoreSslErrors();
            });

    connect(reply, &QNetworkReply::finished, this, [this, reply, id]() {
        QString raw = readReply(reply);
        if (reply->error() != QNetworkReply::NoError) {
            emit errorOccurred(reply->errorString() + "\n" + raw);
        } else {
            emit removeFinished(id, raw.isEmpty() ? "Deleted OK" : raw);
        }
        reply->deleteLater();
    });
}
