import pynetbox

class NBAPI():
    def __init__(self):
        self.__nb = pynetbox.api(
            'http://localhost:8000',
            private_key_file='',
            token=''
        )

if __name__ == "__main__":
    my_app = NBAPI()
