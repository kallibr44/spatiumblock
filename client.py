import json, os, sys, db, core, socket, threading, pickle, time

try:
    import readline
except ImportError:
    import pyreadline as readline
import re,requests
def GetMyIP():
    from netifaces import interfaces, ifaddresses, AF_INET
    for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
            for address in addresses:
                if (address != 'No IP addr') and (address != '127.0.0.1'):
                    adres = (str(addresses)[2:-2])
    return adres
lock = threading.Lock()
#берём адрес хоста
host = GetMyIP()
#инициализируем массив для сохранения входящих клиентов
clients = []
#список "стартовых" нод. |||Сделал по больше, для запаса|||
base_node = [
            ('95.179.166.136', 9090),
            ('185.159.82.212', 9090),
            ('95.27.183.90', 9090),
            ('192.168.1.65', 9090),
            ('192.168.1.66', 9090),
            ('78.46.254.48', 9090),
            ('82.146.44.4', 9090),]

nodes = "node.json"
shutdown = False
#инициализация сокет-объекта
#s1=входящий сокет
s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# пытаемся убить сокет, если он уже активен. Если соект не активен, то иницализируем
try:
    s1.close()
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except Exception:
    pass
s1.bind((host, 9090))
s1.settimeout(1)
s1.setblocking(0)
#s2=исходящий сокет
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# SO_REUSEADDR это ознаает, что на адрес можно подключиться снова даже если он активен
s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# пытаемся убить сокет, если он уже активен. Если соект не активен, то иницализируем
try:
    s2.close()
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except Exception:
    pass
s2.bind((host,0))
s2.settimeout(1)
s2.setblocking(0)
# статус клиента: 0-запуск клиента, 1-работа в оффлайн режиме, 2-подключен к сети
client_status = 0
exit = 0

def get_config(data):
    if data == "wallet":
        return str("test"+str(host))
#коневртация в байты
def ttb(string):
    return bytes(string, encoding='utf-8')
def check_user(ip):
    global clients
    check = 0
    for i in clients:
        if i[0] == ip[0]:
         if i[1] != ip[1]:
            ii = clients.index(i)
            clients.remove(ii)
            clients.append(ip)
            check = 1
        elif i[0] == str(host):
            check = 1
    if ip[0] == str(host):
        check = 1
    if check == 0:
        clients.append(ip)
    else:
        pass

def byte_to_string(bytes):
    return str(bytes.encode("utf-8"))

#ассинхронный поток для принятия входящих сообщений
def receving(sock):
    global shutdown,exit
    while shutdown == False:
        try:
            global clients
            while True:
                #ниже обработка входящих сообщений
                all_data = bytearray()
                while len(all_data) == 0:
                    try:
                        data, addr = sock.recvfrom(2048)
                        """
                        Фикс на статус, если данные удаётся получить, 
                        следовательно клиенты подключились друг к другу.
                        """
                        print('\nСвязь установлена!')
                        global client_status
                        if client_status != 2:
                         client_status = 2
                        #|||
                        if addr[0] != host:
                         check_user(addr)
                        if not data:
                            break
                        all_data = all_data + data
                    except:
                        pass
                if addr[0] != host:
                 print("Запрос от "+str(addr) + " " + str(data.decode("utf-8")))
                 data = data.decode("utf-8")
                 data = data.split("::")
                 threading.Thread(target=sort_data, args=(data, addr,sock,)).start()
        except KeyboardInterrupt:
            shutdown = True
        except:
            pass
    exit = 1

#Здесь обработка входящего сообщения (ассинхронный процесс)
def sort_data(data,addr,sock):
    global clients,c
    if data[0] == "new_event":
        db.check_event(data)
    elif data[0] == "check_db":
        sock.sendto(core.hash(db.get_last_transaction()), addr)
    elif data[0] == "get_peers":
        if len(clients) == 0:
            sock.sendto("peers::None", addr)
        else:
            table = "peers::"
            for i in clients:
             table= str(table + str(i) + ",,")
            sock.sendto(ttb(table), addr)
    elif data[0] == "peers":
        if data[1] == "None":
            print("Новых клиентов не найдено!")
            # init_connection(sock)
        else:
            list = data[1][:-2]
            new_list = list.split(",,")
            for i in new_list:
                if i not in clients:
                 check_user(eval(i))
        next_connection(sock)
    elif data[0] == "ping":
        sock.sendto(bytes("pong::", encoding='utf-8'), addr)
    elif data[0] == "pong":
        c = 1
        sock.sendto(ttb("get_peers::"),addr)
        if addr not in clients:
            clients.append(addr)
    elif data[0] == "pingg":
        sock.sendto(ttb("pongg::"),addr)
    elif data[0] == "quit":
        try:
         clients.remove(addr)
         print("Отключился клиент {0}".format(addr))
        except Exception:
         print("Ошибка. Пользователя нет в базе!")

def next_connection(sock):
    for i in clients:
       if type(i) == tuple:
        # проходим стартовые ноды, если нету клиентов
        text = bytes("pingg::", encoding='utf-8')
        sock.sendto(text, i)
    print("Инициализация закончена!")

#процедура первого подключения при старте (нужно доделать)
def init_connection(sock):
    try:
     f = open(nodes)
     ff = f.readlines()
     #ff=список с нодами
     for i in ff:
        try:
          sock.sendto(bytes("ping::",encoding='utf-8'),i)
          break
        except Exception:
            pass
    except FileNotFoundError:
        for i in base_node:
            # проходим стартовые ноды, если нету клиентов
            if i[0] != host or  i[0] != 'localhost' or i[0] != '':
             text = bytes("ping::", encoding='utf-8')
             try:
              sock.sendto(text,i)
             except:
                pass

#конвертация unix timestamp в формат обычной даты
def date(timestamp):
    import datetime
    return (
        datetime.datetime.fromtimestamp(
            int(timestamp)
        ).strftime('%Y-%m-%d %H:%M:%S')
    )

#инициализирующая функция. сюда добавлять процедуры, которые нужно выполнить на старте программы.
def init():
    global client_status
    try:
        db.init()
        print("Database loaded!")
    except:
        print("Error loading database. Please, reinstall client.")
    client_status = 1
    try:
        threading.Thread(target=receving, args=(s1,)).start()
        threading.Thread(target=receving, args=(s2,)).start()
        init_connection(s2)
    except Exception as e:
        print("Error.")
        print(e)
        pass

def get_status():
    if client_status == 0:
        return "Оффлайн"
    elif client_status == 1:
        return "Поиск пиров..."
    elif client_status == 2:
        return "Подключен к сети"

"""
----------------------------------------------------------------------------------------------------
Ниже идет главный код, все backend функции писать выше
Все frontend функции писать ниже
----------------------------------------------------------------------------------------------------
"""

init()
public_key = db.get_key(get_config("wallet"))
exitt = 0
while exitt == 0:
    try:
        print("Аккаунт: %s\n----------" % public_key)
        print("Статус клиента: %s" % str(get_status()))
        print("IP: {0}".format(host))

        #|||Сделал для удобства и юольшей читабельности. Добавлен 5 пункт который прописан ниже.|||
        message = "1.Отправить сообщение\n" +\
                  "2.Посмотреть последнюю транзакцию\n" +\
                  "3.Посмотреть историю транзакций\n" +\
                  "4.Посмотреть список клиентов\n" +\
                  "5.Проверить последнюю транзакцию\n"

        choose = input(message + ': ')

        if choose == "1":
            text = input("Введите сообщение: ")
            to = input("Получатель: ")
            string = (str(public_key[0]) + ":" + str(core.hash(text,"ergergerfgbfjhrtgaer")) + ":" + str(to))
            try:
                db.add_event(string)
                print("Сообщение отправлено!")
            except:
                print("Ошибка при отправке сообщения!")
        elif choose == "2":
            last_tx = db.get_last_transaction()
            if last_tx is not None:
             print(
                "Последняя транзакция:\nid {0}\nОт кого: {1}\nсообщение: {2}\nКому: {3}\nДата: {4}\n----------------\n".format(
                    last_tx[0], last_tx[1], last_tx[2], last_tx[3], date(last_tx[4])))
            else:
                print("Транзакций не найдено!")
        elif choose == "3":
            wallet = input("Введите свой адрес: ")
            result = db.get_transactions(wallet)
            for i in result:
                print(
                    "id {0}\nОт кого: {1}\nСообщение: {2}\nКому: {3}\nДата: {4}\n----------------\n".format(
                        i[0], i[1], i[2], i[3], date(i[4])))
        elif choose == "4":
            for i in clients:
                print("\n-------\n{0}".format(i))

        #|||Проверка истинности последней транзакции начинается здесь.|||
        elif choose == "5":
            last_tx = db.get_last_transaction()
            if last_tx is not None:
                data = str(last_tx[0]) + str(last_tx[1]) + str(last_tx[2]) + str(last_tx[3]) + str(date(last_tx[4]))
                print("Хеш последней транзакции: " + core.hash_transaction(data))
                truechecker.send_request(clients, host)
            else:
                print("Транзакций не найдено!")

    except KeyboardInterrupt:
        print("Вы действительно хотите выйти? Y/n")
        type = input()
        if type == "N" or type == "n":
            pass
        else:
            shutdown = True
            print("1")
            for i in clients:
                print(i)
                text = bytes("quit::", encoding='utf-8')
                try:
                    s2.sendto(text, (i[0], 9090))
                except:
                    pass
            s1.close()
            s2.close()
            print("2")
            exit = 1
            print("3")
            time.sleep(2)
            print("4")
            while exit == 0:
                pass
            sys.exit(0)
