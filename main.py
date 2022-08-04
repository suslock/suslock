import pathlib, string, secrets, os, time, struct, argparse
from cryptography.fernet import Fernet

appname = 'LockTimer'
appdir = pathlib.Path(os.getenv('APPDATA')) / appname
keyfile = appdir / 'key'
codefile = appdir / 'code'
unlockfile = appdir / 'unlocktime'
unlocktime = float()
is_locked = False
key = b''

def init():
    global key
    global unlocktime
    global is_locked
    os.umask(0o077)
    if not appdir.is_dir():
        appdir.mkdir(mode=0o700)
    else:
        if keyfile.is_file():
            key = load_key()
        if unlockfile.is_file():
            is_locked = True
            unlocktime = read_unlocktime()

def gen_code():
    combination = [secrets.randbelow(10) for x in range(4)]
    return combination

def create_key():
    global key
    key = Fernet.generate_key()
    with open(keyfile, "wb") as data:
        data.write(key)

def load_key():
    key = ''
    with open(keyfile, "rb") as data:
        key = data.read()
    return key 

def write_code(code):
    code_bytes = " ".join([str(x) for x in code]).encode('utf-8')
    f = Fernet(key)
    enc_code = f.encrypt(code_bytes)
    with open(codefile, "wb") as file:
        file.write(enc_code)

def read_code():
    enc_code = b''
    with open(codefile, "rb") as file:
        enc_code = file.read()
    f = Fernet(key)
    code_bytes = f.decrypt(enc_code)
    return code_bytes.decode('utf-8')
    
def write_unlocktime(unlocktime):
    timestr = struct.pack("f", unlocktime)
    with open(unlockfile, "wb") as file:
        file.write(timestr)

def read_unlocktime():
    time_bytes = b''
    with open(unlockfile, "rb") as file:
        time_bytes = file.read()
    unlocktime = struct.unpack('f', time_bytes)
    return unlocktime[0]

def unlock():
    code = str()
    if time.time() > unlocktime:
        code = read_code()
    else:
        print("naughty! you're not allowed to be unlocked yet...")
    print(code)

def get_args():
    parser = argparse.ArgumentParser(description="A program to keep you locked until it's time to unlock ;)")
    parser.add_argument('--unlock', help="attempt to unlock", action='store_true')
    parser.add_argument('--lock', help="generate a code and get locked", action='store_true')
    parser.add_argument('--checktime', help="check how long you have to stay locked", action='store_true')
    parser.add_argument('--clean', help="clean the environment", action='store_true')
    return parser.parse_args()

def cleanup():
    for x in appdir.iterdir():
        if x.is_file():
            x.unlink()

def main():
    global unlocktime
    init()
    args = get_args()

    if args.unlock:
        if is_locked:
            unlock()
        else:
            print('not currently locked!')
    elif args.lock:
        if is_locked:
            sure = input('currently appears you are locked, are you sure?!? (y/N) ')
            if sure.lower() != "y":
                exit(-1)
        cleanup()
        create_key()
        print(key)
        hours_till_unlock = int(input('how many hours do you want to stay locked for? '))
        unlocktime = time.time() + hours_till_unlock * 3600
        write_unlocktime(unlocktime)
        code = gen_code()
        print('generated code: {}'.format([str(x) for x in code]))
        write_code(code)
    elif args.checktime:
        print('unlock time at {}'.format(time.ctime(unlocktime)))
    elif args.clean:
        cleanup()
    else:
        print('no function provided')

if __name__ == "__main__":
    main()