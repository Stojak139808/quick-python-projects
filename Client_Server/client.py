import socket
import time
import os

class Client:

    def __init__(self, server_ip, port):
        self.SERVER = server_ip
        self.PORT = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.on = False

    def run(self):
        
        self.client.connect((self.SERVER, self.PORT))
        #self.client.sendall(bytes("This is from Client",'UTF-16'))
        self.on = True
        while self.on:
            self._menu()
        

    def _menu(self):
        print("Send message - 1\nSend file - 2\nspam - 3\nExit - 4")
        option = input()
        if option == "1":
            self._send_message()
        elif option == "2":
            self._send_file()
        elif option == "3":
            self._spam()
        elif option == "4":
            self._disconnect()
            self.on = False

    def _send_message(self):
        
        out_data = input("Message: ")
        self.client.sendall(out_data.encode('UTF-16'))

    def _send_file(self):
        file = input("File name: ")
        self.client.sendall(chr(2).encode('UTF-16'))  # signal sending file
        in_data = self.client.recv(1024)  # get confirmation
        size = os.path.getsize(file)
        self.client.sendall(file.encode('UTF-16')) # send file name

        in_data = self.client.recv(1024)  # get confirmation

        self.client.sendall(str(size).encode('UTF-16')) # send size
        progress = 0
        # sending the file
        f = open(file, "rb")
        l = f.read(1024)
        print("Sending file...")
        while l:
            self.client.send(l)
            progress += 1024
            print("\r", end="")
            print(progress," / ", size, end="")
            l = f.read(1024)
            #print(l)
        #self.client.send(chr(3).encode('UTF-16'))
        print("\nDone.")


    def _spam(self):

        msg = input("Message: ")
        n = int(input("How many times: "))
        T = float(input("How many fast [s]: "))

        for i in range(n):
            self.client.sendall(msg.encode('UTF-16'))
            time.sleep(T)

    def _disconnect(self):
        self.client.sendall(chr(3).encode('UTF-16'))
        self.client.close()



def main():
    cli = Client("127.0.0.1", 8080)
    cli.run()

if __name__ == "__main__":
    main()