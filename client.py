import json, os, sys, db, core, socks

try:
    import readline
except ImportError:
    import pyreadline as readline
host = socket.gethostbyname(socket.gethostname())
port = 9090
clients = []
base_node = [{'localhost',9090},]

def receving(name, sock):
    while not shutdown:
        try:
            global clients
            while True:
                data, addr = sock.recvfrom(2048)
                if addr not in clients:
                    clients.append(addr)
                print(data.decode("utf-8"))
                data = data.decode("utf-8")
                data = data.split(":")
                if data[0] == "new_event":
                    db.check_event(data)
                elif data[0] == "check_db":
                    pass
        except:
            pass

def init_connection(sock):
    f = open(nodes)
    ff = f.readlines()
    for i in ff:
        try:
          sock.sendto(i)

def date(timestamp):
    import datetime
    return (
        datetime.datetime.fromtimestamp(
            int(timestamp)
        ).strftime('%Y-%m-%d %H:%M:%S')
    )


def init():
    try:
        db.init()
        print("Database loaded!")
    except:
        print("Error loading database. Please, reinstall client.")


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

init()
public_key = db.get_key()
exitt = 0
while exitt == 0:
    try:
        print("Аккаунт: %s" % public_key)
        choose = input(
            "1. Отправить сообщение\n2.Посмотреть последнюю транзакциюn\n3.Посмотреть историю транзакций\n--> ")
        if choose == "1":
            text = input("введите сообщение: ")
            to = input("получатель: ")
            string = (str(public_key[0]) + ":" + str(core.get_hash(str(text).encode('utf-8'))) + ":" + str(to))
            try:
                db.add_event(string)
                print("Сообщение отправлено!")
            except:
                print("ошибка при отправке сообщения!")
        elif choose == "2":
            last_tx = db.get_last_transaction()
            print(
                "Последняя транзакция:\nid {0}\nОт кого: {1}\nсообщение: {2}\nКому: {3}\nДата: {4}\n----------------\n".format(
                    last_tx[0], last_tx[1], last_tx[2], last_tx[3], date(last_tx[4])))
        elif choose == "3":
            wallet = input("Введите свой адрес: ")
            result = db.get_transactions(wallet)
            for i in result:
                print(
                    "id {0}\nОт кого: {1}\nсообщение: {2}\nКому: {3}\nДата: {4}\n----------------\n".format(
                        i[0], i[1], i[2], i[3], date(i[4])))
    except KeyboardInterrupt:
        print("Вы действительно хотите выйти? Y/n")
        type = input()
        if type == "N" or type == "n":
            pass
        else:
            exit = 1
            sys.exit(0)
