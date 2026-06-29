import time
import sys

print("RAM stress test started. Loading RAM to 95%...")
print("Press Ctrl+C to stop.")

blocks = []

try:
    while True:
        block = bytearray(50 * 1024 * 1024)
        blocks.append(block)
        
        total = len(blocks) * 50
        if total % 500 == 0:
            print(f"Allocated: {total} MB")

        import psutil
        ram = psutil.virtual_memory().percent
        print(f"RAM: {ram:.1f}%")
        
        if ram >= 92:
            print("Goal reached (92%+). Holding...")
            while True:
                time.sleep(1)
except KeyboardInterrupt:
    print("\nFreeing memory...")
    blocks.clear()
    time.sleep(1)
    print("Done.")
    sys.exit(0)

