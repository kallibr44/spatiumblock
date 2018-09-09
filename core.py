from Crypto.PublicKey import DSA
from hashlib import sha256
def create_dsa_keys(code):
    key = DSA.generate(1024)
    encrypted_key = key.exportKey(
        passphrase=code,
        pkcs8=True,
        protection="PBKDF2WithHMAC-SHA1AndDES-EDE3-CBC"
    )
    with open("private_rsa_key.bin", "wb") as f:
        f.write(encrypted_key)
    with open("my_rsa_public.pem", "wb") as f:
        f.write(key.publickey().exportKey())
    return key.publickey().exportKey()
code = "somecode"
create_dsa_keys(code)
def hach():
    text=input('введите текст:')
    with open('my_rsa_public.pem', 'r') as file:  # Путь к файлу который нужно прочесть
        var = file.read()  # "Записываем" файл в переменную
        a=var +text
    b=sha256(a.encode()).hexdigest()
    print(b)