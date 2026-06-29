import multiprocessing
import time
import math
import sys
import os

def burn(n):
    # each process pins to a specific core
    print(f"Core {n}: burning...")
    while True:
        x = 0.0001
        for _ in range(50000):
            x = math.sin(x) + math.cos(x) + math.sqrt(abs(x) + 1)
        x ** 0.0001

if __name__ == '__main__':
    multiprocessing.freeze_support()
    print(f"CPU stress test started. Cores: {multiprocessing.cpu_count()}")
    print("Press Ctrl+C to stop.")

    processes = []
    try:
        for i in range(multiprocessing.cpu_count()):
            p = multiprocessing.Process(target=burn, args=(i,))
            p.start()
            processes.append(p)

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        for p in processes:
            p.terminate()
            p.join()
        print("Done.")
        sys.exit(0)
