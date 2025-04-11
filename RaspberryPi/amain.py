# main.py
import threading
import time
import fetch_images 
import fetch  
import encode_recognition_rpi

def fetch_image():
    fetch_images.main()

def run_flask():
    fetch.run_server()

fetch_image();


server_thread2 = threading.Thread(target=run_flask)
server_thread2.daemon = True
server_thread2.start()


print("Server started, waiting for data...")


while True:
    data = fetch.get_data()
    if data:
        print("Data received in main file:", data)
        #server_thread2.stop()
        #server_thread2.daemon = False
        break
    time.sleep(1)

print("Processing the received data...")

encode_recognition_rpi.handle_data(data)
