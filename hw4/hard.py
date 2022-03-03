import time
import queue
from threading import Thread, Timer
import multiprocessing as mp


def A(task_queue, output_conn):
    while True:
        task = task_queue.get()
        result = task.upper()   
        output_conn.send(result)
        time.sleep(5)


def B(input_conn, output_conn):
    def rot13_letter(letter):
        res_ord = ord(letter) + 13
        if res_ord > ord('Z'):
            res_ord -= 26
        return chr(res_ord)

    def rot13(string):
        return "".join(rot13_letter(c) for c in string)

    while True:
        task = input_conn.recv()
        result = rot13(task)
        output_conn.send(result)


def main_routine(a_task_queue, B_res_conn):
    def print_with_time(*args, **kwargs):
        print(f"[{(time.time() % 1000):.2f}]", *args, **kwargs)

    def B_reciever():
        while True:
            try:
                b_msg = B_res_conn.recv()
            except EOFError:
                return
            print_with_time("<B", b_msg)

    def user_inputer():
        while True:
            inp = input()

            if inp == "exit":
                return

            print_with_time("<U", inp)
            try:
                a_task_queue.put_nowait(inp)
                print_with_time(">A", inp)
            except queue.Full:
                print_with_time(
                    "ERROR: unable to send message to A: queue is full")
    
    rec_thread = Thread(target=B_reciever)
    rec_thread.start()
    user_inputer()


def main():
    a_queue = mp.Queue()
    ab_recv_conn, ab_send_conn = mp.Pipe(True)
    bm_recv_conn, bm_send_conn = mp.Pipe(True)

    A_proc = mp.Process(target=A, args=(a_queue, ab_send_conn))
    B_proc = mp.Process(target=B, args=(ab_recv_conn, bm_send_conn))
    A_proc.start()
    B_proc.start()
    main_routine(a_queue, bm_recv_conn)
    A_proc.kill()
    B_proc.kill()

if __name__ == "__main__":
    main()
