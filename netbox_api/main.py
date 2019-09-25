import pynetbox

class NBAPI():
    def __init__(self):
        self.__nb = pynetbox.api(
            'http://localhost:8000',
            private_key_file='key/pk.key',
            token='8ff35cbc1d7e1c4ef6d42e222b913c9f57bf7ed9'
        )

if __name__ == "__main__":
    my_app = NBAPI()
