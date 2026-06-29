import requests, time, threading

BASE = 'http://127.0.0.1:8000'
r = requests.post(f'{BASE}/api/auth/login/', json={'username':'demo','password':'demo123'})
token = r.json()['access']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

r = requests.get(f'{BASE}/api/servers/', headers=headers)
servers = r.json()
sid = servers[0]['id'] if servers else \
    requests.post(f'{BASE}/api/servers/', json={'name':'Test','ip_address':'192.168.1.1'}, headers=headers).json()['id']

ok = fail = 0
lock = threading.Lock()

def agent(n):
    global ok, fail
    for _ in range(10):
        data = {'server': sid, 'cpu_usage': round(50+n*4,1), 'ram_usage': round(40+n*3,1), 'disk_usage': 30}
        r = requests.post(f'{BASE}/api/metrics/', json=data, headers=headers, timeout=5)
        with lock:
            if r.status_code == 201: ok += 1
            else: fail += 1
        time.sleep(0.2)

print('Load test: 5 agents x 10 requests = 50 requests...')
threads = [threading.Thread(target=agent, args=(i,)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print(f'OK: {ok}, Failed: {fail}')
