# 2025_IMAO_DnD_Assistant_ML

### Start Proxy

```
cd ~/Documents/Xray-linux-64
```

```
./xray run -c config.json
```

### venv activation 

```
python3.10 -m venv venv
```

```
source ./venv/bin/activate
``` 

### tmux

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

