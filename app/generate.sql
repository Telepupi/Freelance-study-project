DROP TABLE IF EXISTS reviews, bids, orders, freelancer_profiles, customer_profiles, users, roles, categories;
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT REFERENCES roles(role_id)
);

CREATE TABLE freelancer_profiles (
    freelancer_id INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    contact_method VARCHAR(100),
    about TEXT,
    first_name VARCHAR(100),
    last_name VARCHAR(100)
);

CREATE TABLE customer_profiles (
    customer_id INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    company_name VARCHAR(255),
    contact_method VARCHAR(100)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category_id INT REFERENCES categories(category_id) ON DELETE SET NULL,
    budget INT NOT NULL,
    deadline DATE,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'in_progress', 'completed', 'under_checking')),
    customer_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    freelancer_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bids (
    bid_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    freelancer_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    bid_text TEXT NOT NULL,
    price DECIMAL(12) NOT NULL,
    deadline DATE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    author_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    target_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 10),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO roles (role_name) VALUES
('customer'),
('freelancer'),
('admin');


INSERT INTO users (username, password_hash, role_id) VALUES
('customer1', 'hash1', 1),
('customer2', 'hash2', 1),
('freelancer1', 'hash3', 2),
('freelancer2', 'hash4', 2),
('admin', 'scrypt:32768:8:1$iHyT2aWx3vPSjJQP$0dfdf1bd777a3c5f6d6835f94bc65a0f3e1d11d40f1056ee08f500533e4d28666892d1db588403ee2f7682a3ed2bf49be70287effbb96769bef0d0d0b2add0cd', 3),
('freelancer3', 'hash6', 2),
('freelancer4', 'hash7', 2),
('freelancer5', 'hash8', 2);


INSERT INTO freelancer_profiles (
    freelancer_id, contact_method, about, first_name, last_name
) VALUES
(3, 'telegram: @frontend_guru',
 'Frontend разработчик. 4 года опыта: JavaScript, React, HTML/CSS',
 'Алексей', 'Кузнецов'),

(4, 'email: fs@mail.com',
 'Fullstack разработчик. 6 лет опыта: Python, Django, React, PostgreSQL',
 'Дмитрий', 'Волков'),

(6, 'telegram: @mobile_master',
 'Mobile разработчик. Android (Kotlin) и iOS (Swift), 3 года опыта',
 'Екатерина', 'Морозова'),

(7, 'email: devops@mail.com',
 'DevOps инженер. Docker, Kubernetes, CI/CD, AWS. 5 лет опыта',
 'Сергей', 'Орлов'),

(8, 'telegram: @qa_expert',
 'QA инженер. Manual + Automation (Python, Selenium), 4 года опыта',
 'Анна', 'Романова');


INSERT INTO customer_profiles (customer_id, company_name, contact_method) VALUES
(1, 'TechCorp', 'email: contact@techcorp.com'),
(2, 'DevStar', 'telegram: @devstar_support');

INSERT INTO categories (name, description) VALUES
('Web Development', 'Создание и разработка сайтов'),
('Design', 'Графический и UI/UX дизайн'),
('Mobile Apps', 'Разработка мобильных приложений'),
('Backend', 'Серверная разработка');

INSERT INTO orders (title, description, category_id, budget, deadline, status, customer_id, freelancer_id) VALUES
('Создать сайт-визитку', 'Нужен простой сайт-визитка на 3–4 страницы.', 1, 15000, '2025-03-01', 'active', 1, NULL),
('Дизайн мобильного приложения', 'Требуется UI/UX дизайн для приложения.', 2, 30000, '2025-03-10', 'in_progress', 2, NULL),
('API для мобильного приложения', 'Разработать REST API на Flask.', 1, 40000, '2025-02-25', 'in_progress', 1, 4),
('Редизайн лендинга', 'Нужно обновить дизайн лендинга компании.', 2, 20000, '2025-03-15', 'active', 2, NULL);


INSERT INTO bids (order_id, freelancer_id, bid_text, price, deadline, status) VALUES
(1, 1, 'Могу сделать сайт-визитку за 10 дней.', 14000, '2025-02-28', 'pending'),
(1, 2, 'Сделаю быстро и качественно.', 15000, '2025-03-01', 'pending'),
(2, 3, 'Готова выполнить дизайн в срок.', 28000, '2025-03-08', 'pending'),
(3, 4, 'API сделан, доработаю оставшееся.', 40000, '2025-02-25', 'accepted');

INSERT INTO reviews (author_id, target_id, order_id, rating, review_text) VALUES
(1, 3, 3, 10, 'Отличная работа, API выполнен качественно.'),
(2, 4, 2, 9, 'Дизайн выполнен хорошо, но немного задержался срок.');
