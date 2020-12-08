DROP TABLE IF EXISTS facilities;
DROP TABLE IF EXISTS users;

CREATE TABLE facilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    check_date DATE,
    owner TEXT NOT NULL,
    sector INTEGER NOT NULL,
    criticality_category INTEGER
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT UNIQUE NOT NULL
);

INSERT INTO facilities
    (name, check_date, owner, sector, criticality_category)
VALUES
    ('ТЕЦ-5', NULL, 'username1', 1, NULL),
    ('Хлібозавод Кулінічи', NULL, 'username2', 4, NULL),
    ('Безлюдівський мясокомбінат', NULL, 'username1', 4, NULL),
    ('Артемівський лікеро-горілчаний завод', NULL, 'username2', 3, NULL),
    ('Завод Поршень', NULL, 'username1', 8, NULL),
    ('Завод Турбоатом', NULL, 'username2', 8, NULL);

INSERT INTO users
    (username, password)
VALUES
    ('username1', '123'),
    ('username2', '1234');

