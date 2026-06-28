# VPS Monitor — Вопросы и ответы для защиты

## 1. Общие вопросы по проекту

### Q1: Что за проект?
Это Django REST API + агент для мониторинга VPS серверов. Агент собирает CPU/RAM/Disk каждые 10 секунд и шлет на сервер. При превышении порога (90%) создается Alert и приходит уведомление в Telegram.

### Q2: Из каких частей состоит?
- **agents.py** — скрипт на VPS, собирает метрики psutil и шлет POST
- **config/** — настройки Django (settings, urls, wsgi)
- **users/** — регистрация + JWT логин
- **servers/** — CRUD серверов
- **metrics/** — получение метрик, алерты, Telegram

### Q3: Какая архитектура?
```
agents.py (на VPS) 
    │  POST /api/metrics/ (каждые 10 сек)
    ▼
Django API (DRF + PostgreSQL)
    │
    ▼
check_and_create_alert()
    │
    ├── Alert в БД
    └── Telegram уведомление
```

---

## 2. Модели (models.py)

### Q4: Какие модели есть и как они связаны?
Три модели:
- **User** (встроенная Django) — один ко многим → Server
- **Server** (owner, name, ip_address) — один ко многим → Metric, Alert
- **Metric** (server, cpu_usage, ram_usage, disk_usage) 
- **Alert** (server, message, level, created_at)

Связи: `User 1──* Server 1──* Metric` и `Server 1──* Alert`

### Q5: Почему Metric и Alert раздельные модели?
Metric хранит **историю** замеров (проценты + время). Alert — **событие** о превышении порога. Можно посмотреть график метрик и список алертов отдельно.

### Q6: Какие типы полей используются?
- `FloatField` — cpu_usage, ram_usage, disk_usage
- `CharField` — name, message, level
- `GenericIPAddressField` — ip_address
- `TextField` — description
- `DateTimeField(auto_now_add=True)` — created_at
- `ForeignKey` — server (связь), owner

---

## 3. Агент (agents.py)

### Q7: Как агент собирает данные?
Через psutil:
```python
psutil.cpu_percent(interval=1)      # загрузка CPU за 1 сек
psutil.virtual_memory().percent     # RAM в процентах
psutil.disk_usage('/').percent      # диск в процентах
```

### Q8: Как часто шлет метрики?
Каждые 10 секунд: `time.sleep(10)` в бесконечном цикле `while True`.

### Q9: Как агент авторизуется?
JWT токен записан прямо в коде: `Authorization: Bearer <token>`. Токен получается от `/api/auth/login/` и хардкодится.

### Q10: Почему токен протухает и что делать?
В settings.py `ACCESS_TOKEN_LIFETIME = 15 минут`. Через 15 минут запросы начнут падать с 401. Нужно либо:
- добавить обновление токена по refresh
- переделать на API-ключ без срока
- увеличить lifetime

### Q11: Что будет, если сервер недоступен?
`requests.post` выбросит исключение (ConnectionError, Timeout), программа упадет. Обработки ошибок в agents.py нет.

---

## 4. Аутентификация (users/)

### Q12: Какие эндпоинты аутентификации?
```
POST /api/auth/register/       — создать пользователя (AllowAny)
POST /api/auth/login/          — получить access + refresh токены
POST /api/auth/login/refresh/  — обновить access токен
```

### Q13: Как работает JWT?
POST login → Django проверяет username+password → возвращает два токена:
- **access** (15 мин) — кладется в заголовок `Authorization: Bearer <token>`
- **refresh** (7 дней) — для получения нового access

### Q14: Какая разница между access и refresh токенами?
Access — короткоживущий (15 мин), передается в каждом запросе. Refresh — долгий (7 дней), хранится безопасно, используется только для обновления access.

### Q15: Почему регистрация доступна всем?
`permission_classes = [AllowAny]` — чтобы новый пользователь мог зарегистрироваться без токена. Иначе получится замкнутый круг: для регистрации нужен токен, для токена нужна регистрация.

---

## 5. Серверы (servers/)

### Q16: Какие эндпоинты для серверов?
```
GET  /api/servers/            — список своих серверов
POST /api/servers/            — создать сервер
GET  /api/servers/<id>/      — детали сервера
```

### Q17: Как гарантируется, что пользователь видит только свои серверы?
В `get_queryset()` фильтр: `Server.objects.filter(owner=self.request.user)`. Токен привязывает запрос к конкретному пользователю.

### Q18: Что такое `perform_create`?
Метод, вызываемый после валидации но перед сохранением. Здесь проставляется `owner=self.request.user` — владелец сервера.

---

## 6. Метрики и алерты (metrics/) — САМОЕ ВАЖНОЕ

### Q19: Какие эндпоинты?
```
POST /api/metrics/           — создать метрику (агент)
GET  /api/metrics/alerts/    — список алертов пользователя
```

### Q20: Опиши полный цикл обработки метрики.
1. Агент шлет POST с JSON: `{server: 3, cpu_usage: 95, ram_usage: 87, disk_usage: 72}`
2. `MetricSerializer` валидирует (0-100%)
3. `MetricCreateView.perform_create` сохраняет метрику
4. `check_and_create_alert` проверяет пороги
5. Если > 90% — создается `Alert` в БД + Telegram

### Q21: Как работают алерты?
```python
def check_and_create_alert(self, metric):
    if metric.cpu_usage > 90:
        Alert.objects.create(server=metric.server, message=f"CPU: {metric.cpu_usage}%", level='critical')
        send_telegram_alert(f"CRITICAL - {metric.server.name} - CPU: {metric.cpu_usage}%")
    if metric.ram_usage > 90:
        # то же для RAM
    # disk_usage НЕ ПРОВЕРЯЕТСЯ
```

### Q22: Почему disk_usage не проверяется?
Ошибка в коде. Агент шлет disk_usage, модель его хранит, но `check_and_create_alert` не проверяет. Можно было исправить добавлением одного `if`.

### Q23: Что делает сериализатор?
Проверяет что cpu_usage, ram_usage, disk_usage в диапазоне 0-100. Преобразует JSON в объект Python/Django и обратно.

### Q24: Зачем в AlertListView нужна проверка swagger_fake_view?
```python
if getattr(self, 'swagger_fake_view', False):
    return Alert.objects.none()
```
drf-yasg при генерации Swagger UI вызывает `get_queryset()` без аутентификации. Без этой проверки упадет ошибка, потому что `self.request.user` не существует. Это костыль для Swagger.

---

## 7. Настройки (settings.py)

### Q25: Какая база данных используется?
PostgreSQL. Настройки: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_HOST — из `.env` файла.

### Q26: Зачем CORS_ALLOW_ALL_ORIGINS = True?
Разрешить запросы с любого домена. Нужно, если фронтенд (React/Vue) будет на отдельном сервере или порту. В продакшне лучше ограничить конкретными доменами.

### Q27: Почему ALLOWED_HOSTS = ['*']?
Разрешить запросы с любых хостов. В продакшне нужно указать конкретный домен.

### Q28: Какие библиотеки используются?
- `djangorestframework` — REST API
- `djangorestframework-simplejwt` — JWT токены
- `django-cors-headers` — CORS
- `drf-yasg` — Swagger документация
- `psutil` — сбор метрик (в агенте)
- `python-dotenv` — загрузка .env
- `requests` — HTTP запросы (агент + Telegram)

---

## 8. Telegram

### Q29: Как работает Telegram уведомление?
```python
def send_telegram_alert(message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})
```
Отправляет POST запрос к Telegram Bot API с текстом сообщения.

### Q30: Почему алерт может быть в БД но не прийти в Telegram?
В коде `try/except RequestException: pass` — если Telegram недоступен, ошибка проглатывается. Алерт в БД создан, но Telegram не отправлен.

---

## 9. Коварные вопросы

### Q31: В чем главная проблема агента?
Токен захардкожен. Через 15 минут (lifetime access токена) он протухнет и агент перестанет работать. Никакой логики обновления нет.

### Q32: Что будет, если запустить два agents.py одновременно?
Оба будут слать метрики с одним `SERVER_ID`. В БД будут дублирующиеся записи.

### Q33: Как понять, что сервер умер?
Никак. Если агент падает или сервер выключается — перестают приходить метрики, но API об этом не узнает. Нужен heartbeat — проверка, что метрик не было > N минут.

### Q34: Один пользователь может удалить чужой сервер?
Нет. Эндпоинта DELETE вообще нет. Есть только GET (список/детали) и POST (создание).

### Q35: Почему нет эндпоинтов PUT/PATCH/DELETE для серверов?
Автор не реализовал. Есть только создание и просмотр.

### Q36: Что вернет GET /api/servers/ если у пользователя нет серверов?
Пустой список `[]`. `filter(owner=user)` вернет пустой QuerySet.

### Q37: Как масштабировать на 1000 серверов?
Сейчас агент шлет все на один сервер. Для 1000 серверов нужно:
- нагрузка: 1000 POST/10 сек = 100 RPS
- выделенный сервер под Django
- возможно, очередь задач (Celery) для алертов

### Q38: Что произойдет при SQL injection?
Django ORM защищает от SQL injection, если не использовать `raw()`.

### Q39: Почему пароль хранится безопасно?
`User.objects.create_user()` хэширует пароль. В БД хранится не `password`, а хэш.

---

## 10. Что можно улучшить (ответы на "что бы ты добавил")

1. **Disk usage alerts** — добавить `if metric.disk_usage > 90` 
2. **Refresh токена в агенте** — чтобы не протухал
3. **Celery** — асинхронная отправка Telegram
4. **Warning уровень** — например, > 75% = warning, > 90% = critical
5. **Heartbeat** — проверка, что сервер жив
6. **DELETE/PUT серверов** — полный CRUD
7. **Лимит history метрик** — удалять старые метрики (например, старше 30 дней)
8. **Тесты** — в tests.py пусто
9. **Docker** — для простого деплоя
10. **n8n/auth** — не хардкодить токен в agents.py
