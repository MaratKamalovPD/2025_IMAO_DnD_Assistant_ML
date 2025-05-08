# 2025_IMAO_DnD_Assistant_ML

## Общая информация

### Создание и активация виртуального окружения

```
python3.10 -m venv venv
```

```
source ./venv/bin/activate
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