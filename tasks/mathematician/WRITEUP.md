# Великий математик: Write-up

В условии дан файл `recovered-001.pyc`. Это — байт-код интерпретатора Python. Этот факт можно выяснить, поискав расширение в интернете или воспользовавшись утилитой `file`.

Запустить файл можно обычным интерпретатором Python, но ничего хорошего не выйдет:

```
$ python3 recovered-001.pyc 
Traceback (most recent call last):
  File "s3cr3t_5c13nc3_j0b.py", line 34, in <module>
  File "s3cr3t_5c13nc3_j0b.py", line 24, in main
  File "s3cr3t_5c13nc3_j0b.py", line 15, in get
  File "s3cr3t_5c13nc3_j0b.py", line 8, in get
  File "s3cr3t_5c13nc3_j0b.py", line 8, in get
  File "s3cr3t_5c13nc3_j0b.py", line 8, in get
  [Previous line repeated 993 more times]
  File "s3cr3t_5c13nc3_j0b.py", line 5, in get
RecursionError: maximum recursion depth exceeded in comparison
```

Программа завершилась с ошибкой. Если поискать причину ошибки в интернете, то мы узнаем, что разработчикам рекомендуют увеличивать максимальную глубину рекурсии или изменять алгоритм. Нам этот вариант не подходит, ведь код скомпилирован и вносить изменения в него мы не можем. Существует несколько вариантов решения этой проблемы.

## Вариант 1. Подключение библиотеки

Любой Python-файл можно подключить как библиотеку. Таким образом, мы можем написать программу, которая использует этот файл как библиотеку, при этом увеличить глубину рекурсии в нашей программе.

```python
import sys
sys.setrecursionlimit(1000000)

import recovered-001
```

Однако это не запустится — имя библиотеки с дефисом недопустимо. Переименуем файл в `lib.pyc` и заменим импорт. Код всё ещё не работает. В тексте ошибки мы видим, что в самом начале была вызвана функция `main`, и она уже вызывала функцию `get` рекурсивно. Попробуем вызвать её:

```python
import sys
sys.setrecursionlimit(1000000)

import lib
lib.main()
```

На этот раз программа запускается корректно и выдаёт флаг.

## Вариант 2. Декомпиляция

Как и во многих других интерпретируемых языках, из байт-кода Python можно получить исходный код программы. Для этого воспользуемся декомпилятором [uncompyle6](https://github.com/rocky/python-uncompyle6):

```python
$ uncompyle6 recovered-001.pyc
# uncompyle6 version 3.6.7
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.9 (default, Apr 18 2020, 01:56:04) 
# [GCC 8.4.0]
# Embedded file name: s3cr3t_5c13nc3_j0b.py
# Compiled at: 2020-05-12 15:07:24
# Size of source mod 2**32: 743 bytes
import codecs, sys

def get(a, b):
    if a >= b:
        arg1 = a - b
        arg2 = b
        return get(arg1, arg2)
    else:
        if a == 0:
            return b
        arg1 = b
        arg2 = a
        return get(arg1, arg2)


def main():
    p = 141580561079899551495863961821657129836209787581446581591644772592702997327951089250862884804191
    q = 1960488988283273938139146527554511410430619016713952671501925432811038301783489211411712019324411835
    print('Calculating result, wait....', end='\r', flush=True)
    scientific_result = get(p, q)
    print('Result is calculated!       ', flush=True)
    hexad = hex(scientific_result)[2:]
    print('Got:', (codecs.decode(hexad, 'hex')), flush=True)


if __name__ == '__main__':
    main()
# okay decompiling recovered-001.pyc
```

Мы видим, что в коде задаются два числа `p` и `q`, после чего выполняется функция `get`, которая и вызывает рекурсию. С результатом функции проводятся какие-то вычисления, приводящие к строке с флагом.

Если внимательно присмотреться к рекурсивным вычислениям, можно заметить аналогию с известным многим со школы *алгоритмом Евклида с вычитаниями* — этот алгоритм ищет наибольший общий делитель двух чисел.

Опять же, можно взять получившийся код и увеличить глубину рекурсии, а можно воспользоваться эффективной функцией `gcd` из модуля `math`, переписав код следующим образом:

```python
import codecs
import math

def main():
    p = 141580561079899551495863961821657129836209787581446581591644772592702997327951089250862884804191
    q = 1960488988283273938139146527554511410430619016713952671501925432811038301783489211411712019324411835
    print('Calculating result, wait....', end='\r', flush=True)
    scientific_result = math.gcd(p, q)
    print('Result is calculated!       ', flush=True)
    hexad = hex(scientific_result)[2:]
    print('Got:', (codecs.decode(hexad, 'hex')), flush=True)


if __name__ == '__main__':
    main()
```

Выполнение этого кода также приводит к получению флага.

Флаг: **ugra_weird_gcd_calculation_a95eb29327c3**.
