-- Initialize database for Pet Shop application
CREATE DATABASE IF NOT EXISTS petshop_db;
CREATE USER IF NOT EXISTS 'petshop_user'@'%' IDENTIFIED BY 'petshop_password';
GRANT ALL PRIVILEGES ON petshop_db.* TO 'petshop_user'@'%';
FLUSH PRIVILEGES; 