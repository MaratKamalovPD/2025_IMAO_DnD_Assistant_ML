# 2025_IMAO_DnD_Assistant_ML

## Общая информация

### Создание и активация виртуального окружения

```
python3.10 -m venv venv
```

```
source ./venv/bin/activate
``` 

или 

```
python3.10 -m venv venv_open_router
``` 

```
source ./venv_open_router/bin/activate
``` 

```
pip install -r ./actions_processor_llm/requirements.txt
```

или 

```
python3.10 -m venv venv_bestiary_img
``` 

```
source ./venv_bestiary_img/bin/activate
``` 

```
pip install -r ./bestiary_images_scripts/requirements.txt
```

## battle_description_ms

gRPC микросевис для получения описания сражений

Для работы требуется `secrets.json` с прокси 

### Формат файла `secrets.json`

Файл `secrets.json` используется для хранения API-ключей OpenAI и соответствующих прокси-серверов.

#### Пример содержимого:

```json
{
    "api_keys_with_proxies": [
        {
            "api_key": "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxx",
            "proxy": "socks5://username:password@127.0.0.1:5000"
        },
        {
            "api_key": "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxx",
            "proxy": "socks5://username:password@127.0.0.1:5000"
        }
    ]
}
```
### Для запуска

```bash
python3 battle_description_ms/main.py
```

### Для локального теста

```bash
python3 battle_description_ms/client.py
```

## creature_generator

**ТЕКУЩИЙ КОД НЕ РАБОТАЕТ С MONGO С TLS, нужно это как-то поправить**

http сервис запускаемый на VM вне РФ для походов в API Gemini

### Start Proxy 

Для API Gemini не работает, но может быть полезно для других API, работающих по http, а не по gRPC

```bash
cd ~/Documents/Xray-linux-64
```

```bash
./xray run -c config.json
```

### tmux (для запуска асинхронной сессии через SSH терминал)

Запуск сессии:

 ```bash
tmux
``` 

Запускай Flask:
 ```bash
python3 creature_generator/main.py
``` 

Чтобы выйти из tmux, не останавливая процессы:

Запускай Flask:
 ```bash
Ctrl + b, затем d
``` 

Чтобы снова зайти в сессию:

 ```bash
tmux attach
``` 

## bestiary_images_scripts

#### change_http_to_https_for_img.py

подключается к MongoDB и заменяет старые URL изображений в коллекции на новые

#### cv2_test.py

сравнивает два изображения с помощью SIFT и визуализирует область совпадения на втором изображении

#### cv2_test_2.py

находит фрагмент на изображении с помощью SIFT, обрезает его и сохраняет как `.webp` с сохранением прозрачности

#### final_parse_script.py

обрабатывает список существ из `bestiary_data.json` в параллельных процессах.  
  Для каждого существа делает запрос к API, загружает изображения в MinIO (S3), обновляет ссылки в JSON и сохраняет результат в MongoDB.  
  Использует `multiprocessing` для повышения производительности и `tqdm` для отображения прогресса.  
  ⚠️ Возможен deadlock при большом числе процессов из-за особенностей работы python клиента MongoDB с `multiprocessing`

#### mongo_db_delete_three_and_more.py

обрезает массив `images` в каждом документе MongoDB до первых двух элементов, если их больше

#### mongo_db_test.py

загружает данные из `bestiary_data.json` в MongoDB и позволяет выполнять поиск существ по русскому имени

#### mongo_db_test_2.py

выводит общее количество документов в коллекции `creatures` и показывает первые 5 из них

#### processing_images_400x300.py

извлекает фрагмент с помощью SIFT из пар изображений, загруженных из MinIO (S3), и сохраняет его обратно в S3, а затем обновляет соответствующий документ в MongoDB.  
  Скрипт:
  - Подключается к MongoDB и получает коллекцию с документами существ.
  - Для каждой записи берёт первую (иконку) и вторую (оригинал) картинки из поля `images`.
  - Загружает изображения из S3 и находит область соответствия между ними с помощью алгоритма SIFT и гомографии.
  - Автоматически адаптирует масштаб выделенной области, если изображение оказывается слишком маленьким.
  - Обрезает, масштабирует и сохраняет полученный фрагмент в формате WebP (с сохранением альфа-канала, если он есть).
  - Загружает результат в S3 в папку `processed` и дописывает URL в массив `images` соответствующего Mongo-документа.
  - При ошибках записи (например, некорректная декодировка) — логирует информацию в файл `error_log.txt`.

📌 Используется для генерации финальных изображений с прозрачностью

#### s3_test.py

получает JSON с API, загружает изображение в MinIO (S3), обновляет ссылку и сохраняет модифицированный JSON на диск

#### web_crawler_1.py

скачивает все url-адреса страниц существ из бестиария с API `ttg.club`, объединяет в один список и сохраняет как `bestiary_data.json`

## actions_processor_llm

```bash
py -3.10 -m venv venv_open_router
```
```bash
venv_open_router\Scripts\activate 
```
```bash
pip install -r .\actions_processor_llm\requirements.txt
```

gRPC микросевис для получения действий существа в виде распаршеной структуры

Для работы требуется `secrets.json` с прокси 

### Формат файла `secrets.json`

Файл `secrets.json` используется для хранения API-ключей OpenAI и соответствующих прокси-серверов.

#### Пример содержимого:

```json
{
    "api_keys_with_proxies": [
        {
            "api_key": "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxx",
            "proxy": "socks5://username:password@127.0.0.1:5000"
        },
        {
            "api_key": "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxx",
            "proxy": "socks5://username:password@127.0.0.1:5000"
        }
    ]
}
```
### Для запуска

```bash
python3 battle_description_ms/main.py
```

### Для локального теста

```bash
python3 battle_description_ms/client.py
```