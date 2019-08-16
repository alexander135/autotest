# Report Portal
## Развертывание

1. На машину с установленным Docker необходимо скопировать проект из Gitlab
```
git clone git_adress
```
2. Во избежание конфликтов создадим сеть в которой будут работать наши контейнеры
```
 docker network create -d bridge --subnet=192.168.112.0/20 --gateway=192.168.112.1 autotest_net
```
Subnet И gateway выбирайте исходя из своих возможностей. Если имя autotest_net вас не устраивает измените его и исправьте строчку в docker-compose.yaml 

```
networks:
  net:
    external: 
      name: autotest_net
```   
 
Так же есть возможность не создавать новую сеть, а использовать сеть по умолчанию 172.20.0.0/16. Для этого удалите строки external и name  из docker-compose.yaml
```
    external: 
      name: autotest_net
```
3. Для доступа к mongo и jenkins необходимо создать юзеровю Для этого в папке проекта создаем файл .env следующего содержания:
```
mongo_login=Admin
mongo_password=Password11
jen_login=reporter
jen_pass=reporter
```
Где mongo_login и mongo_password можно переименовать как вам угодно


4. Переходим в папку проекта и выполняем команды
```
docker-compose build
docker-compose up
```
После чего на экране появятся логи. Приложение развернуто успешно при появлении примерно такого сообщения:
```
web_1         |  * Serving Flask app "server" (lazy loading)
web_1         |  * Environment: production
web_1         |    WARNING: Do not use the development server in a production environment.
web_1         |    Use a production WSGI server instead.
web_1         |  * Debug mode: on
web_1         |  * Running on http://web:80/ (Press CTRL+C to quit)""
```

5. Доступ к серверу осуществляется по порту указанному в docker-compose.yaml
```
    ports: 
      - "80:80"
```
# Изменение

1. Для добавления новых job из Jenkins в систему необходимо добавить в файл uir/config.yaml в поле  ```job:```  код следующего вида:
```
  name_of_job_to_add:                              #имя джобы
    chart_data_count: 10
    color:
      bot: 95
      top: 90
    id: 0
    pk: 0
    to_sum:            #данные каких тестов суммировать для второй таблицы
      1:
      - Tests
      - SmokeTests
      2:
      - FunctionalTests
```
Кроме имени джобы и тестов для суммирования ничего менять не стоит

Для добавления в LCOV в поле ```LCOV:``` дописываем следующее:
```
  any_name_you_want:
    id: '0'
    path: path_to_page_with_lcov
    pk: 0
```
Для добавления джоб в другие разделы скорее всего требуется написание нового скрипта.

2. Для создания бекапа базы данных выполняем следующие команды из папки проекта:
```
docker-compose exec db sh
mongodump -u login_for_mongo -p password for mongo
CRTL+d
```
Восстановление базы данных производится автоматически при старте docker-compose. Если нужно восстановить БД вручную выполняем следующее:
```
docker-compose exec db sh
mongorestore -u login_for_mongo -p password for mongo
CTRL+d
```
Для доступа к самой mongo выполняем следующее:
```
docker-compose exec db sh
mongo -u login_for_mongo -p password_for_mongo
```
