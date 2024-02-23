CREATE DATABASE pythontest;
CREATE USER 'pythontest'@'localhost' IDENTIFIED WITH mysql_native_password by 'Testtest991!';
GRANT ALL PRIVILEGES ON pythontest.* TO 'pythontest'@'localhost';