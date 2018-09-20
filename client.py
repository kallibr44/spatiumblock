import json, os, sys, db, core, socket,threading,pickle

try:
    import readline
except ImportError:
    import pyreadline as readline
import re,requests
def GetMyIP():
    text = requests.get('http://edonkey2000.com/').text()
    return re.search(r'\d+\.\d+\.\d+\.\d+', text).group()
#берём адрес хоста
#host = socket.gethostbyname(socket.gethostname())
host = GetMyIP()
#host = 'localhost'
#если клиент ключевой, порт указывать статический, если это обычный клиент, порт=0
port = 0
#port=9090
#инициализируем массив для сохранения входящих клиентов
clients = []
#список "стартовых" нод.
base_node = [('82.146.44.4', 9090),]
nodes = "node.json"
shutdown = False
#инициализация сокет-объекта
print(host)
print(port)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)
# статус клиента: 0-запуск клиента, 1-работа в оффлайн режиме, 2-подключен к сети
client_status = 0
def get_config(data):
    if data == "wallet":
        return str("test"+str(host))
#коневртация в байты
def text_to_byte(string):
    return bytes(string)

def byte_to_string(bytes):
    return str(bytes.encode("utf-8"))
#ассинхронный поток для принятия входящих сообщений
def receving(sock):
    global shutdown
    while not shutdown:
        try:
            global clients
            while True:
                #ниже обработка входящих сообщений
                all_data = bytearray()
                while len(all_data) == 0:
                    try:
                        data, addr = sock.recvfrom(2048)
                        if addr not in clients:
                            clients.append(addr)
                        if not data:
                            break
                        all_data = all_data + data
                    except:
                        pass
                if addr not in clients:
                    clients.append(addr)
                    print("Новй клиент " + addr)
                print("Запрос от "+str(addr) + " " + str(data.decode("utf-8")))
                data = data.decode("utf-8")
                data = data.split(":")
                threading.Thread(target=sort_data,args=(data,addr,sock,)).start()
        except KeyboardInterrupt:
            shutdown = True
        except:
            pass

#Здесь обработка входящего сообщения (ассинхронный процесс)
def sort_data(data,addr,sock):
    global clients
    if data[0] == "new_event":
        db.check_event(data)
    elif data[0] == "check_db":
        sock.sendto(str(db.get_last_transaction()), addr)
    elif data[0] == "get_peers":
        if len(clients) == 0:
            sock.sendto("peers:None", addr)
        else:
            table = clients
            new_data = [{"type": "peers"}, {table}]
            tex = pickle.dumps(new_data)
            sock.sendto(tex, addr)
    elif data[0] == "peers":
        if data[1] == "None":
            print("Новых клиентов не найдено!")
            # init_connection(sock)
        else:
            list = data[1]
            for i in list:
                clients.append(i)
    elif data[0] == "ping":
        sock.sendto(bytes("pong:", encoding='utf-8'), addr)
    elif data[0] == "pong":
        if addr not in clients:
            clients.append(addr)
#процедура первого подключения при старте (нужно доделать)
def init_connection(sock):
    try:
     f = open(nodes)
     ff = f.readlines()
     #ff=список с нодами
     for i in ff:
        try:
          sock.sendto(bytes("ping:",encoding='utf-8'),i)
          break
        except Exception:
            pass
    except FileNotFoundError:
        for i in base_node:
            # проходим стартовые ноды, если нету клиентов
            print(i)
            text = bytes("ping:", encoding='utf-8')
            sock.sendto(text,i)

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
        rT = threading.Thread(target=receving, args=(s,))
        rT.start()
        init_connection(s)
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
        choose = input(
            "1. Отправить сообщение\n2.Посмотреть последнюю транзакцию\n3.Посмотреть историю транзакций\n4. Посмотреть список клиентов\n--> ")
        if choose == "1":
            text = input("введите сообщение: ")
            to = input("получатель: ")
            string = (str(public_key[0]) + ":" + str(core.hash(text,"ergergerfgbfjhrtgaer")) + ":" + str(to))
            try:
                db.add_event(string)
                print("Сообщение отправлено!")
            except:
                print("ошибка при отправке сообщения!")
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
                    "id {0}\nОт кого: {1}\nсообщение: {2}\nКому: {3}\nДата: {4}\n----------------\n".format(
                        i[0], i[1], i[2], i[3], date(i[4])))
        elif choose == "4":
            for i in clients:
                print("\n-------\n{0}".format(i))
    except KeyboardInterrupt:
        print("Вы действительно хотите выйти? Y/n")
        type = input()
        if type == "N" or type == "n":
            pass
        else:
            s.close()
            exit = 1
            sys.exit(0)
