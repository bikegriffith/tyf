from multiprocessing import Process, Queue
import subprocess


def f(q, pid):
    print("Starting process {}".format(pid))
    result = subprocess.run(['python3', 'schedule.py'], stdout=subprocess.PIPE)
    print("Process {} finished".format(pid))
    q.put(result.stdout)


if __name__ == '__main__':
    q = Queue()

    for num in range(10):
        Process(target=f, args=(q, num)).start()

    print(q.get().decode('utf-8'))
