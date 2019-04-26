# autotest
install all requirements from requirements.txt using 
```
 pip install req_name
```
server uses mongo to store test results. So you have to install it using 
```
brew install mongodb-community@4.0.8
brew services start mongodb-community@4.0.8
```
on Mac or 
```
sudo apt-get install -y mongodb-org=4.0.8 mongodb-org-server=4.0.9 mongodb-org-shell=4.0.8 mongodb-org-mongos=4.0.8 mongodb-org-tools=4.0.8
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections
sudo service mongod start
```
on ubuntu

to change default port open /usr/local/etc/mongod.conf on Mac or /etc/mongodb.conf on Ubuntu and make some changes in net:


```
net:
  bindIp: 127.0.0.1
  port: 80
```

restart service
```
brew services restart mongodb-community
````

or
```
sudo service mongod restart
```

and change port number in config.yaml
```
db:
  host: "127.0.0.1"
  port: 27017
  ```
to use bd use:
```
mongo --port port_number
```
if you don't use --port than 27017 will be used

to get acces to jenkins edit path to Jenkins, username and password in config.yaml
