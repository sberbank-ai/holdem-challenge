# Руководство по созданию ботов

## Подготовка решения к отправке

В проверяющую систему необходимо отправить код бота, запакованный в ZIP-архив. 

Пример архивов:
- [example-python-bot.zip](https://drive.google.com/file/d/0B7WVjmSt-QObWWx0a000aE16NVU/view?usp=sharing)
- [example-cpp-bot.zip](https://drive.google.com/file/d/0B7WVjmSt-QObZDJGT3FtTzVPTUk/view?usp=sharing)

В корне архива обязательно должен быть файл metadata.json следующего содержания:
```json
{
    "image": "sberbank/python",
    "entry_point": "python bot.py"
}
```

Здесь `image` — название docker-образ, в котором будет запускаться решение, `entry_point` — команда, при помощи которой необходимо запустить решение. При этом для решения текущей директорией будет являться корень архива — вы можете положить туда рядом файлы.

Для запуска решения доступны следующие образы:
- `sberbank/python` — Python3 с установленным большим набором библиотек
- `gcc` - для запуска компилируемых C/C++ решений ([подробнее здесь](https://github.com/sberbank-ai/holdem-challenge/blob/master/GUIDE_CPP.md))
- `node` — для запуска JavaScript
- `openjdk` — для Java
- `mono` — для C#

Подойдет любой другой образ, доступный для загрузки из DockerHub. 

Исполняемая команда обменивается с симулятором игры через stdin/stdout. Симулятор передает по одному событию в строчке stdin, в формате `event_type<\t>data`, где `data` — JSON-объект с параметрами события. [Пример входных данных](simulator_stdin_example.jsonlines), которые симулятор подает в stdin. [Описание событий и их параметров](PyPokerEngine/AI_CALLBACK_FORMAT.md).

В ответ на событие `declare_action` бот должен в отведенное время ответить в stdout строчкой в формате:
```
action<\t>amount
```
здесь `action` — одно из доступных игроку действий (fold, call, raise), `amount` — количество фишек для действия raise, 0 в остальных случаях.

В случае использования буферизованного ввода/вывода, не забудьте сбрасывать буфер (`flush()`) после записи действия в stdout. Иначе, симулятор может не получить сообщение и у бота выйдет лимит по времени.

## Python

Разработку бота на языке Python удобнее всего делать с помощью библиотеки [PyPokerEngine](./PyPokerEngine). Для этого необходимо создать класс, который наследует `pypokerengine.players.BasePokerPlayer` и переопределяет его методы. 

В примере [examples/python-bot](https://github.com/sberbank-ai/holdem-challenge/blob/master/examples/python-bot) реализована обертка, позволяющая сделать из класса бота исполняемый скрипт, соответствующий интерфейсу симулятора.

Для запуска ботов на языке Python рекомендуется использовать образ `sberbank/python`, в котором установлен Python 3, а также большой набор библиотек, включая `PyPokerEngine`, `numpy`, `scipy`, `pandas`.


## C/C++

Обратите внимание на [инструкцию по запуску ботов на компилируемых языках](GUIDE_CPP.md).

