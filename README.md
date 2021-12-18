# yamdb_final
![yamdb_final](https://github.com/VadimKharyukov/yamdb_final/actions/workflows/main.yml/badge.svg)

Это учебно-практический проект студента ЯндексПрактикума направления бекэнд
 разработки.Цель проекта создание API для социальной сети Yatube.Проект интегрирован в Docker.
***
####Возможности:
* Создавать посты и редактировать посты
* Добавлять к постам картинки и комментарии
* Отслеживать интересющего вас пользователя
* Просто общаться

### Как запустить проект:


```
https://github.com/VadimKharyukov/yamdb_final.git
```
### Как установить проект:
1. Установка Docker, docker-compose можно найти в официальной статье.
2. Заполнить фаил окружения .env из template файла в той же директории.
3. Собрать и запустить контейнер.
```
docker-compose up -d --build
```
4.Миграции.

```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```
5. Сбор статитики.
```
docker-compose exec web python manage.py collectstatic --no-input
```
