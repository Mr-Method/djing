# djing
Попытка интернет биллинга. djing сокращение от django-billing. Это web интерфейс управления абонентами интернет-провайдера.
Сейчас идёт тестирвоание работы на Mikrotik, функционал пока минимальный, т.к. пишу в свободное время. Работа планируется в реальных условиях и на реальных абонентах.
Использовано python 3, django 1.9, bootstrap 3, и другое в файле requirements.txt
Может:
  Наблюдать за устройствами по snmp
  Отправлять изменения мгновенно на mikrotik
  Привязывать на карте к точкам топологии устройства
  Есть привязка монтажника к группам абонентов
  Есть менеджер задач на абонентов. Это оператор может выбрать абонента и описать проблему. Система отправит оповещение через telegram ответственному за групу указанного абонента монтажнику с текстом проблемы, адресом и телефоном абонента.

## Установка(не завершил описание):
На ArchLinux нужые пакеты я устанавливаю так:
```
# pacman -Sy mariadb-clients python3 python-pip nginx uwsgi
```
Дальше ставим всё для python через pip:
```
# pip install git+https://github.com/nerosketch/djing.git
```

На Fedora ставил так
```
# dnf install uwsgi python3 python3-devel nginx python-pip git redis mariadb mariadb-devel net-snmp net-snmp-devel gcc redhat-rpm-config
# pip3 install rq mysqlclient easysnmp xmltodict netaddr telepot Pillow Django==1.9
```
