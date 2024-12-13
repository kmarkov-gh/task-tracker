-- Подключаемся к базе данных
\c taskdb

-- Создаем таблицу, если она еще не существует
CREATE TABLE IF NOT EXISTS tasks (
id SERIAL PRIMARY KEY,
title VARCHAR(100) NOT NULL,
description TEXT,
status VARCHAR(50) DEFAULT 'pending',
due_date DATE
);

-- Вставляем тестовые данные, если их еще нет
INSERT INTO tasks (title, description, status, due_date)
SELECT * FROM (VALUES
('Setup environment', 'Prepare Docker environment for PostgreSQL and application.', 'completed', '2024-12-01'::date),
('Design API', 'Define and implement FastAPI routes for task CRUD.', 'in progress', '2024-12-05'::date),
('Write documentation', 'Document the API using Swagger.', 'pending', '2024-12-10'::date)
) AS new_tasks(title, description, status, due_date)
WHERE NOT EXISTS (SELECT 1 FROM tasks);
