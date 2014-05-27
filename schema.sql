PRAGMA FOREIGN_KEYS=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS subscriber;
CREATE TABLE subscriber (
    subs_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL UNIQUE,
    ipaddr VARCHAR NOT NULL UNIQUE,
    calling_id VARCHAR NOT NULL,
    called_id VARCHAR NOT NULL,
    imsi CHAR(15) NOT NULL,
    imei CHAR(16) NOT NULL,
    loc_info VARCHAR NOT NULL,
    conn_id INTEGER,
    enabled INTEGER
);
DROP TABLE IF EXISTS connection;
CREATE TABLE connection (
    conn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    speed_down INTEGER,
    speed_up INTEGER,
    speed_var REAL,
    latency_up INTEGER,
    latency_down INTEGER,
    latency_jitter INTEGER,
    loss_down REAL,
    loss_up REAL,
    loss_jitter REAL
);
DROP TABLE IF EXISTS settings;
CREATE TABLE settings (
    rad_ip VARCHAR NOT NULL,
    rad_port INTEGER NOT NULL DEFAULT 1813,
    rad_user VARCHAR NOT NULL,
    rad_pass VARCHAR NOT NULL,
    rad_secret VARCHAR NOT NULL
);
DROP TABLE IF EXISTS client;
CREATE TABLE client (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    conn_id INTEGER DEFAULT 1,
    subs_id INTEGER,
    FOREIGN KEY(subs_id) REFERENCES subscriber(subs_id) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO settings(rad_ip, rad_port, rad_user, rad_pass, rad_secret) VALUES ("10.0.16.1", 1813, "admin", "password", "secret");

INSERT INTO connection(name, description, speed_down, speed_up, speed_var, latency_up,
    latency_down, latency_jitter, loss_down, loss_up, loss_jitter) VALUES ("4G/LTE",
    "4G/LTE technology allows for high troughput with low latency and low packet loss rates", 20000, 20000, 5000, 50, 50, 10, 0.01, 0.01, 0.005);
INSERT INTO connection(name, description, speed_down, speed_up, speed_var, latency_up,
    latency_down, latency_jitter, loss_down, loss_up, loss_jitter) VALUES ("3G",
    "HSPA Connections are quicker than 2G Connections, but are still suffering from high latency and high loss rates. ",4000, 1000, 500, 50, 50, 20, 0.1, 0.1, 0.05);
INSERT INTO connection(name, description, speed_down, speed_up, speed_var, latency_up,
    latency_down, latency_jitter, loss_down, loss_up, loss_jitter) VALUES ("2.5G",
    "GPRS Connections are slow and lossy", 236.8, 59.3, 2, 150, 150, 20, 1, 1, 0.5);

INSERT INTO connection(name, description, speed_down, speed_up, speed_var, latency_up,
    latency_down, latency_jitter, loss_down, loss_up, loss_jitter) VALUES ("2G",
    "GPRS Connections are slow and lossy", 9.6, 9.6, 2, 150, 150, 20, 1, 1, 0.5);

INSERT INTO subscriber(name, ipaddr, calling_id, called_id, imsi, imei, loc_info, conn_id, enabled) VALUES ("Marie", "10.0.0.10",
    "004917489639813", "web.apn", "90125827556293", "66619348724005", "seattle", 1, 0);
INSERT INTO subscriber(name, ipaddr, calling_id, called_id, imsi, imei, loc_info, conn_id, enabled) VALUES ("John", "10.0.0.20",
    "004916705353340", "iphone.apn", "90108576436201", "66669498626395", "london", 2, 0);
INSERT INTO subscriber(name, ipaddr, calling_id, called_id, imsi, imei, loc_info, conn_id, enabled) VALUES ("Linus", "10.0.0.30",
    "004916636129410", "internet.apn", "90156451177704", "66657422830175", "stockholm", 3, 0);
INSERT INTO subscriber(name, ipaddr, calling_id, called_id, imsi, imei, loc_info, conn_id, enabled) VALUES ("Alex", "10.0.0.40",
    "004412345678901", "telepathy.apn", "90156451177999", "66657422830999", "bishkek", 3, 0);
COMMIT;
