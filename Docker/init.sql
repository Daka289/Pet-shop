-- Initialize PostgreSQL database for Pet Shop application
CREATE USER petshop_user WITH ENCRYPTED PASSWORD 'petshop_password';
CREATE DATABASE petshop_db OWNER petshop_user;
GRANT ALL PRIVILEGES ON DATABASE petshop_db TO petshop_user;