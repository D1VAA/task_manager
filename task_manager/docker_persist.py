from time import sleep

def default():
    sleep(5)
    default()
if __name__ == '__main__':
    default()