import os
import socket
import threading
import time
from db import connect_database
from dotenv import load_dotenv

load_dotenv()

server_lock = threading.Lock()

IP = "127.0.0.1"
PORT = 45999
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
SERVER_DATA_PATH = "Server_data"
CLIENT_DATA_PATH = "Client_data"


db_message, user_col = connect_database()
print(db_message)


def get_unique_name(file_name, folder_path):
    base_name, extension = os.path.splitext(file_name)
    new_name = file_name
    count = 1

    while os.path.exists(os.path.join(folder_path, new_name)):
        new_name = f"{base_name}({count}){extension}"
        count += 1

    return new_name


def check_file_exist_or_not():
    if not os.path.exists(SERVER_DATA_PATH):
        os.makedirs(SERVER_DATA_PATH)

    if not os.path.exists(CLIENT_DATA_PATH):
        os.makedirs(CLIENT_DATA_PATH)


def main():
    check_file_exist_or_not()
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
            print(f"[ERROR] Connection failed: {e}")


def handle_client(conn, addr):
    print(f"[CONNECTING] Client {addr} is connected")
    try:
        while True:
            client_data = conn.recv(SIZE).decode(FORMAT)
            if not client_data:
                break
            key, name, pw = client_data.split("/")
            if key == "Login":
                with server_lock:
                    login_result = handle_login(name, pw)
                conn.sendall(login_result.encode(FORMAT))
                if login_result == "Login success":
                    handle_client_requests(conn, addr)
                    break
            elif key == "SignUp":
                with server_lock:
                    sign_up_result = handle_sign_up(name, pw)
                conn.sendall(sign_up_result.encode(FORMAT))
    except Exception as e:
        print(f"[ERROR] Client handling failed: {e}")
        conn.close()
    except:
        print("User close app")
        conn.close()


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
            if not data:
                break
            cmd, name = data.split("/")
            if cmd == "Upload":
                handle_upload(name, conn)
            elif cmd == "Download":
                handle_download(name, conn)
            else:
                print(f"[DISCONNECT] Client {addr} is disconnected")
                break
    except Exception as e:
        print(f"[DISCONNECT] Client {addr} disconnected: {e}")
    finally:
        conn.close()


def handle_upload(file_name, conn):
    unique_name = get_unique_name(file_name, SERVER_DATA_PATH)
    num_of_segments = int(conn.recv(SIZE).decode(FORMAT))
    segments = [None] * num_of_segments

    signal = 0

    while signal == 0:
        with server_lock:
            signal = recv_segment(conn, segments, num_of_segments)

    print("[RECEIVE ALL SEGMENTS]")
    merge_result = merge_segments_into_file(segments, unique_name)
    conn.sendall(merge_result.encode(FORMAT))
    conn.recv(SIZE)
    conn.sendall(unique_name.encode(FORMAT))


def recv_segment(conn, segments, num_of_segments):
    for _ in range(num_of_segments):
        while True:
            try:
                segment_index = int(conn.recv(SIZE).decode(FORMAT))
                conn.sendall("ok".encode(FORMAT))
                segment = conn.recv(SIZE)
                segments[segment_index] = segment
                conn.sendall(f"ack {segment_index}".encode(FORMAT))
                break
            except:
                conn.sendall(f"nak {segment_index}".encode(FORMAT))
                print(f"Error receiving segment {segment_index}: Retrying...")
    return 1


def merge_segments_into_file(segments, file_name):
    try:
        file_path = os.path.join(SERVER_DATA_PATH, file_name)
        with server_lock:
            with open(file_path, "wb") as f:
                for segment in segments:
                    f.write(segment)
        print("[MERGE SUCCESS] merge segments into file successfully")
        return "SUCCESS"
    except:
        print("[MERGE FAIL] merge segments into file fail")
        return "FAIL"


def handle_download(file_name, conn):
    unique_name = get_unique_name(file_name, CLIENT_DATA_PATH)
    file_path = os.path.join(SERVER_DATA_PATH, file_name)
    if os.path.exists(file_path):
        segments = divide_file_into_segments(file_path, conn)
        create_segment_thread(segments, conn)

        send_msg = "Download all segments successfully"
        print(send_msg)

        conn.sendall(unique_name.encode(FORMAT))

    else:
        print(f"ERROR: File {file_name} not found")
        conn.sendall("CAN'T FOUND".encode(FORMAT))


def divide_file_into_segments(file_path, conn):
    with server_lock:
        with open(file_path, "rb") as f:
            file_data = f.read()
    file_size = len(file_data)
    segments = [file_data[i : i + SIZE] for i in range(0, file_size, SIZE)]
    conn.sendall(f"{len(segments)}".encode(FORMAT))
    return segments


def create_segment_thread(segments, conn):
    threads = []
    for index, segment in enumerate(segments):
        t = threading.Thread(target=send_segment, args=(index, segment, conn))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def send_segment(segment_index, segment, conn):
    while True:
        try:
            with server_lock:
                conn.sendall(f"{segment_index}".encode(FORMAT))
                conn.recv(SIZE)
                conn.sendall(segment)
                recv_msg = conn.recv(SIZE).decode(FORMAT)
                key, index = recv_msg.split(" ")
                if key == "ack" and int(index) == segment_index:
                    print(f"ack {segment_index}")
                    break
                else:
                    print(f"nak {segment_index}")
                    time.sleep(0.5)
                    continue
        except Exception as e:
            print(f"Error sending segment {segment_index}: {e}. Retrying...")


if __name__ == "__main__":
    main()
