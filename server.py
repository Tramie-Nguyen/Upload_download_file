import os
import socket
import threading
import time
from db import connect_database
from dotenv import load_dotenv

load_dotenv()

IP = "127.0.0.1"
PORT = 4567
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
SERVER_DATA_PATH = "Server_data"
CLIENT_DATA_PATH = "Client_data"
RECEIVE = []
CHECK = []

db_message, user_col = connect_database()
print(db_message)

if not os.path.exists(SERVER_DATA_PATH):
    os.makedirs(SERVER_DATA_PATH)

if not os.path.exists(CLIENT_DATA_PATH):
    os.makedirs(CLIENT_DATA_PATH)


def main():
    print("SERVER SIDE:")
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[STARTING] Server is starting...")
    server_s.bind(ADDR)
    server_s.listen()
    print("[LISTENING] Server is listening...")
    while True:
        try:
            conn, addr = server_s.accept()
            thr = threading.Thread(target=handle_client, args=(conn, addr))
            thr.start()
        except Exception as e:
            print(f"[ERROR] Connected fail: {e}")


def handle_client(conn, addr):
    print(f"[CONNECTING] Client {addr} is connected")
    try:
        while True:
            client_data = conn.recv(SIZE).decode(FORMAT)
            key, name, pw = client_data.split("/")
            if key == "Login":
                login_result = handle_login(name, pw)
                conn.sendall(login_result.encode(FORMAT))
                if login_result == "Login success":
                    handle_client_requests(conn, addr)
                    break
            elif key == "SignUp":
                sign_up_result = handle_sign_up(name, pw)
                conn.sendall(sign_up_result.encode(FORMAT))
    except:
        print("User close app")


def handle_login(name, pw):
    user = user_col.find_one({"name": name})
    if user:
        if user["password"] == pw:
            return "Login success"
        else:
            return "Wrong password"
    else:
        return "Account doesn't exist"


def handle_sign_up(name, pw):
    user = user_col.find_one({"name": name})
    if user:
        return "Already has this name"
    else:
        user_col.insert_one({"name": name, "password": pw})
        return "Sign up success"


def handle_client_requests(conn, addr):
    try:
        while True:
            data = conn.recv(SIZE).decode(FORMAT)
            print("RECEIVE FILE")
            if not data:
                break
            cmd, name = data.split("/")
            if cmd == "Upload":
                upload_file(name, conn)
            elif cmd == "Download":
                download_file(name, conn)
            else:
                print("[DISCONNECT] client {} is disconnected ".format(addr))
                break
    except Exception as e:
        print(f"[DISCONNECT] client {addr} is disconnected ")
    conn.close()


def upload_file(file_name, conn):
    num_of_segments = int(conn.recv(SIZE).decode(FORMAT))
    segments = [None] * num_of_segments
    global RECEIVE
    RECEIVE = [0] * num_of_segments
    signal = 0
    while signal == 0:
        signal = recv_segment(conn, segments)
    print("[RECEIVE ALL SEGMENTS]")
    merge_result = merge_segments_into_file(segments, file_name)
    conn.sendall(merge_result.encode(FORMAT))


def recv_segment(conn, segments):
    segment_index = conn.recv(SIZE).decode(FORMAT)
    if segment_index == "Upload all segments successfully":
        return 1
    segment_index = int(segment_index)
    try:
        if RECEIVE[segment_index] == 0:
            segments[segment_index] = conn.recv(SIZE)
        else:
            ignore = conn.recv(SIZE)
        conn.sendall(f"ack {segment_index}".encode(FORMAT))
        RECEIVE[segment_index] = 1
    except:
        conn.sendall(f"nack{segment_index}".encode(FORMAT))
    return 0


def merge_segments_into_file(segments, file_name):
    try:
        file_path = os.path.join(SERVER_DATA_PATH, file_name)
        with open(file_path, "wb") as f:
            for segment in segments:
                f.write(segment)
        print("[MERGE SUCCESS] merge segments into file successfully")
        return "SUCCESS"
    except:
        print("[MERGE FAIL] merge segments into file fail")
        return "FAIL"


def download_file(file_name, conn):
    file_path = os.path.join(SERVER_DATA_PATH, file_name)
    if os.path.exists(file_path):
        segments = divide_file_into_segments(file_path, conn)
        while 0 in CHECK:
            create_segment_thread(segments, conn)
        send_msg = "Download all segments successfully"
        print(send_msg)
        conn.sendall(send_msg.encode(FORMAT))
        merge_result = conn.recv(SIZE).decode(FORMAT)
        print(merge_result)
    else:
        error_msg = f"ERROR: File {file_name} not found"
        print(error_msg)
        conn.sendall("CAN'T FOUND".encode(FORMAT))


def divide_file_into_segments(file_path, conn):
    with open(file_path, "rb") as f:
        file_data = f.read()

    file_size = len(file_data)
    segments = [file_data[i : i + SIZE] for i in range(0, file_size, SIZE)]
    global CHECK
    CHECK.clear()
    CHECK = [0] * len(segments)
    conn.sendall(f"{len(segments)}".encode(FORMAT))
    create_segment_thread(segments, conn)
    return segments


def create_segment_thread(segments, conn):
    threads = []
    for index, segment in enumerate(segments):
        if CHECK[index] == 1:
            continue
        else:
            t = threading.Thread(target=send_segment, args=(index, segment, conn))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()


def send_segment(segment_index, segment, conn):
    conn.sendall(f"{segment_index}".encode(FORMAT))
    conn.sendall(segment)
    recv_msg = conn.recv(SIZE).decode(FORMAT)
    key, index = recv_msg.split(" ")
    if key == "ack" and int(index) == segment_index:
        CHECK[segment_index] = 1
    time.sleep(0.1)


if __name__ == "__main__":
    main()
