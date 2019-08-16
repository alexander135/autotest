# Report Portal
## Развертывание

1. На машину с установленным Docker необходимо скопировать проект из Gitlab
'''
git clone git_adress
'''
2. Во избежание конфликтов создадим сеть в которой будут работать наши контейнеры
'''
 docker network create -d bridge --subnet=192.168.112.0/20 --gateway=192.168.112.1 autotest_net
'''
Subnet И gateway выбирайте исходя из своих возможностей. Если имя autotest_net вас не устраивает измените его и исправьте строчку в docker-compose.yaml 
'''

networks:
  net:
    external: 
      name: autotest_net
'''   
 
Так же есть возможность не создавать новую сеть, а использовать сеть по умолчанию 172.20.0.0/16. Для этого удалите строки external и name  из docker-compose.yaml
'''
    external: 
      name: autotest_net
'''
3. Переходим в папку проекта и выполняем команды
'''
docker-compose build
docker-compose up
'''
После чего на экране появятся логи. Приложение развернуто успешно при появлении примерно такого сообщения:
'''
web_1         |  * Serving Flask app "server" (lazy loading)
web_1         |  * Environment: production
web_1         |    WARNING: Do not use the development server in a production environment.
web_1         |    Use a production WSGI server instead.
web_1         |  * Debug mode: on
web_1         |  * Running on http://web:80/ (Press CTRL+C to quit)""
'''

4. Доступ к серверу осуществляется по порту указанному в docker-compose.yaml
'''
    ports: 
      - "80:80"
'''

