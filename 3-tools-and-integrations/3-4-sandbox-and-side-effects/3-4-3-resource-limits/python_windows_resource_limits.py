import multiprocessing


def task():
    while True:
        pass


if __name__ == "__main__":
    p = multiprocessing.Process(target=task)
    p.start()
    p.join(timeout=5)
    if p.is_alive():
        print("Time limit exceeded")
        p.terminate()
