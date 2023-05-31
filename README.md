
<a id='start_page'></a>
# <p align=center>Foodgram</p>
#### *<p align=center>Проект "Продуктовый помощник"<br>Онлайн сервис и API*</p>
___
<!---
![](https://github.com/A-Rogachev/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
-->
![readmeimage2](https://github.com/A-Rogachev/foodgram-project-react/assets/97498636/39fc0a03-b4d9-426e-9bc6-d8daa16d5a9c)
- Любой пользователь может зарегистрироваться на сервисе (используется адрес электронной почты). 
- Без регистрации можно просматривать отдельные страницы рецептов и страницы пользователей; фильтровать рецепты по тегам.
- Регистрация дает возможность создавать, редактировать и удалять рецепты; добавлять понравившиеся рецепты в список избранного; подписываться на авторов; работать с персональным списком покупок - доступна выгрузка файла с количеством необходимых ингредиентов для рецептов из списка покупок.
- Вход в систему осуществляется с помощью логина и пароля (пароль можно изменить в любой момент).


  
  [![](https://img.shields.io/badge/Python-3.7.9-blue)](https://www.python.org/downloads/release/python-379/) [![](https://img.shields.io/badge/Django-3.2.16-green)](https://docs.djangoproject.com/en/4.1/releases/3.2.16/) [![](https://img.shields.io/badge/DRF-3.2.14-orange)](https://www.django-rest-framework.org/community/release-notes/#3124) [![](https://img.shields.io/badge/Docker-24.0.1-yellow)](https://docs.docker.com/engine/install/ubuntu/)

#### Запуск проекта локально с использованием технологии Docker:

1. Клонировать репозиторий и перейти в него в терминале/командной строке:
   ```
   git clone https://github.com/A-Rogachev/foodgram-project-react.git
   cd foodgram-project-react/infra/
   ```
2. В текущей директории создать файл *.env* с необходимыми переменными окружениями (можно использовать значения, указанные ниже):

   ```
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgrespass
   DB_HOST=db
   DB_PORT=5432
   ```

3. Развернуть проект:
   
   ```
   docker-compose up
   ```

4. Выполнить миграции, создать суперпользователя:

```
docker exec -it web bash
(запуск bash контейнера следует производить в новом окне терминала)
```
```
python manage.py migrate                  (выполнение миграций)
```
```
python manage.py createsuperuser          (создание суперпользователя)
```
5. Загрузка статики (необходимо для корректного отображения панели администрирования и документации):
```
python manage.py collectstatic --no-input
```
6. Заполнить БД начальными данными можно с помощью следующей команды:
```
python manage.py load_initial_data ingredients.json  (загрузка ингредиентов)
```

### <p align=center>*После успешного запуска проекта, будут доступны следующие эндпойнты API:*</p>
##### Эндпойнты, доступные после регистрации отмечены знаком ( ! )
```
/api/users/ -> GET: получение списка пользователей
/api/users/ -> POST: создание нового пользователя (!)
/api/users/{id}/ -> GET: профиль пользователя (!)
/api/users/me/ -> GET: личный профиль (!)
/api/users/set_password/ -> POST: изменение пароля пользователя (!)
/api/auth/token/login/ -> POST: получение токена авторизации (!)
/api/auth/token/logout/ -> POST: удаление токена текущего пользователя (!)
```
```
/api/tags/ -> GET: получение списка тегов
/api/tags/{id}/ -> GET: получение тега по его уникальному идентификатору
```
```
/api/ingredients/ -> GET: получение списка ингредиентов
/api/ingredients/{id}/ -> GET: получение ингредиента по его уникальному идентификатору
```
```
/api/recipes/ -> GET: получение списка рецептов
/api/recipes/ -> POST: публикация нового рецепта (!)
/api/recipes/{id}/ -> GET: получение рецепта по его уникальному идентификатору
/api/recipes/{id}/ -> PATCH: обновление рецепта (только для автора рецепта) (!)
/api/recipes/{id}/ -> DELETE: удаление рецепта (только для автора рецепта) (!)
```
```
/api/recipes/{id}/favorite/ -> POST: добавление рецепта в избранное (!)
/api/recipes/{id}/favorite/ -> DELETE: удаление рецепта из избранного (!)
```
```
/api/users/subscriptions/ -> GET: получение личного списка подписок (!)
/api/users/{id}/subscribe/ -> POST: подписка на пользователя по уникальному идентификатору (!)
/api/users/{id}/subscribe/ -> DELETE: отписка от пользователя по уникальному идентификатору (!)
```
```
/api/recipes/download_shopping_cart/ -> GET: получение списка покупок (!)
/api/recipes/{id}/shopping_cart/ -> POST: добавление ингредиентов рецепта в список покупок (!)
/api/recipes/{id}/shopping_cart/ -> DELETE: удаление ингредиентов рецепта из списка покупок (!)
```

#### Автор

> <font size=2>Рогачев Александр
> Студент факультета Бэкенд. Когорта № 50</font>

[наверх](#start_page)
