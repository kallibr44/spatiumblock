from Crypto.PublicKey import DSA
import hashlib, binascii


def create_dsa_keys(code):
    key = DSA.generate(1024)
    encrypted_key = key.exportKey(
        passphrase=code,
        pkcs8=True,
        protection="PBKDF2WithHMAC-SHA1AndDES-EDE3-CBC"
    )
    with open("private_dsa_key.bin", "wb") as f:
        f.write(encrypted_key)
    with open("my_dsa_public.pem", "wb") as f:
        f.write(key.publickey().exportKey('DSA'))
    return key.publickey().exportKey('DSA')


def hash(password, salt):
    dk = hashlib.pbkdf2_hmac('sha256', b'password', b'salt', 100000)
    # Взврат вычисленного значения
    return binascii.hexlify(dk)


# Для тестирования ниже примеры вызовов (далее использовать по назначению)
# Вызов процедуры генерации ключей
#print(create_dsa_keys(input("Press random keys:\n")))
# Вызов процедуры вычисления хэш-значения
#print(hash(input("Enter password:\n"), input("Enter salt:\n")))

