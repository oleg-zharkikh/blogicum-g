
import time
import functools
from datetime import datetime, timedelta


def seconds_until_next_retry(now: datetime) -> int:
    weekday = now.weekday()  # 0 = Monday, 5 = Saturday, 6 = Sunday

    # будний день и рабочее время 09:00–17:00
    if weekday < 5 and 9 <= now.hour < 17:
        return 30 * 60  # 30 минут

    # иначе — ждать до 10:00 понедельника
    days_ahead = (7 - weekday) % 7
    if days_ahead == 0:
        days_ahead = 7

    next_monday = (now + timedelta(days=days_ahead)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )

    return int((next_monday - now).total_seconds())


def retry_with_wait(max_attempts: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt >= max_attempts:
                        raise

                    now = datetime.now()
                    wait_seconds = seconds_until_next_retry(now)

                    print(
                        f"Попытка {attempt} не удалась: {e}. "
                        f"Следующая попытка через {wait_seconds // 60} минут."
                    )

                    time.sleep(wait_seconds)
                    attempt += 1

        return wrapper
    return decorator
    
    
    
    usage

    
@retry_with_wait(max_attempts=5)
def unstable_job():
    print("Выполняю задачу...")
    raise RuntimeError("Временная ошибка")


    



pip install statsmodels pandas numpy matplotlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.api import SimpleExpSmoothing, Holt
import warnings
warnings.filterwarnings('ignore')

# Исходные данные
data = [13, 10, 7, 17, 5, 13, 3, 9, 2, 7, 5, 6, 1, 0, 3]

# Создаем временной ряд (предположим, что это 15 месяцев подряд)
dates = pd.date_range(start='2023-01-01', periods=len(data), freq='M')
ts = pd.Series(data, index=dates)

print("Исходный временной ряд:")
print(ts)
print(f"\nДлина ряда: {len(ts)} месяцев")

# Метод 1: Скользящее среднее (простой метод выделения тренда)
window_size = 3  # размер окна для сглаживания
ts_trend_ma = ts.rolling(window=window_size, center=True, min_periods=1).mean()

# Метод 2: Экспоненциальное сглаживание
model_ses = SimpleExpSmoothing(ts).fit(smoothing_level=0.3)
ts_trend_ses = model_ses.fittedvalues

# Метод 3: Модель Холта (двойное экспоненциальное сглаживание) для тренда
model_holt = Holt(ts).fit(smoothing_level=0.3, smoothing_trend=0.1)
ts_trend_holt = model_holt.fittedvalues

# Метод 4: Линейный тренд через регрессию (предполагаем линейный тренд)
# Создаем числовые значения для времени
X = np.arange(len(ts)).reshape(-1, 1)
y = ts.values

from sklearn.linear_model import LinearRegression
model_lr = LinearRegression()
model_lr.fit(X, y)
linear_trend = model_lr.predict(X)

# Метод 5: Декомпозиция временного ряда (если есть сезонность)
# Для короткого ряда используем аддитивную модель
try:
    decomposition = seasonal_decompose(ts, model='additive', period=3)  # period - предполагаемая сезонность
    trend_decompose = decomposition.trend
except:
    trend_decompose = None
    print("\nПримечание: декомпозиция может быть неточной для такого короткого ряда")

# Визуализация
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Анализ тренда временного ряда публикаций', fontsize=16)

# Исходный ряд
axes[0, 0].plot(ts, marker='o', label='Исходные данные')
axes[0, 0].plot(ts_trend_ma, color='red', linewidth=2, label=f'Скользящее среднее (окно={window_size})')
axes[0, 0].set_title('Метод 1: Скользящее среднее')
axes[0, 0].set_xlabel('Месяц')
axes[0, 0].set_ylabel('Число публикаций')
axes[0, 0].legend()
axes[0, 0].grid(True)

# Экспоненциальное сглаживание
axes[0, 1].plot(ts, marker='o', label='Исходные данные')
axes[0, 1].plot(ts_trend_ses, color='green', linewidth=2, label='Экспоненциальное сглаживание')
axes[0, 1].set_title('Метод 2: Экспоненциальное сглаживание')
axes[0, 1].set_xlabel('Месяц')
axes[0, 1].set_ylabel('Число публикаций')
axes[0, 1].legend()
axes[0, 1].grid(True)

# Модель Холта и линейный тренд
axes[1, 0].plot(ts, marker='o', label='Исходные данные')
axes[1, 0].plot(ts_trend_holt, color='purple', linewidth=2, label='Модель Холта')
axes[1, 0].plot(ts.index, linear_trend, color='orange', linestyle='--', linewidth=2, label='Линейный тренд')
axes[1, 0].set_title('Метод 3: Модель Холта и линейный тренд')
axes[1, 0].set_xlabel('Месяц')
axes[1, 0].set_ylabel('Число публикаций')
axes[1, 0].legend()
axes[1, 0].grid(True)

# Декомпозиция (если доступна)
if trend_decompose is not None:
    axes[1, 1].plot(ts, marker='o', alpha=0.5, label='Исходные данные')
    axes[1, 1].plot(trend_decompose, color='brown', linewidth=3, label='Тренд (декомпозиция)')
    axes[1, 1].set_title('Метод 4: Декомпозиция временного ряда')
    axes[1, 1].set_xlabel('Месяц')
    axes[1, 1].set_ylabel('Число публикаций')
else:
    axes[1, 1].text(0.5, 0.5, 'Декомпозиция не выполнена\n(слишком короткий ряд)', 
                    ha='center', va='center', transform=axes[1, 1].transAxes)
    axes[1, 1].set_title('Метод 4: Декомпозиция временного ряда')
axes[1, 1].legend()
axes[1, 1].grid(True)

plt.tight_layout()
plt.show()

# Анализ результатов
print("\n" + "="*60)
print("АНАЛИЗ ТРЕНДА:")
print("="*60)

# Анализ линейного тренда
print(f"\n1. Линейный тренд:")
print(f"   Уравнение: y = {model_lr.intercept_:.2f} + {model_lr.coef_[0]:.2f} * t")
print(f"   Коэффициент наклона: {model_lr.coef_[0]:.2f}")

if model_lr.coef_[0] > 0:
    print("   Интерпретация: наблюдается СРЕДНИЙ РОСТ числа публикаций")
elif model_lr.coef_[0] < 0:
    print("   Интерпретация: наблюдается СРЕДНЕЕ СНИЖЕНИЕ числа публикаций")
else:
    print("   Интерпретация: тренд ОТСУТСТВУЕТ")

# Сравнение начала и конца ряда
print(f"\n2. Сравнение начала и конца ряда:")
print(f"   Среднее за первые 3 месяца: {np.mean(data[:3]):.1f}")
print(f"   Среднее за последние 3 месяца: {np.mean(data[-3:]):.1f}")

change = ((np.mean(data[-3:]) - np.mean(data[:3])) / np.mean(data[:3])) * 100
print(f"   Изменение: {change:.1f}%")

if change > 10:
    print("   Интерпретация: ЗНАЧИТЕЛЬНЫЙ РОСТ")
elif change < -10:
    print("   Интерпретация: ЗНАЧИТЕЛЬНОЕ СНИЖЕНИЕ")
else:
    print("   Интерпретация: СТАБИЛЬНАЯ СИТУАЦИЯ (без резких изменений)")

# Прогноз на следующий период
print(f"\n3. Прогноз на следующий месяц (линейная модель):")
next_month = len(ts)
forecast = model_lr.predict([[next_month]])[0]
print(f"   Прогнозируемое число публикаций: {forecast:.1f}")
print(f"   Диапазон вероятных значений: [{max(0, forecast-5):.1f}, {forecast+5:.1f}]")

# Общий вывод
print(f"\n4. ОБЩИЙ ВЫВОД:")
if model_lr.coef_[0] < -0.5 and change < -20:
    print("   📉 Наблюдается ЯВНАЯ НИСХОДЯЩАЯ ТЕНДЕНЦИЯ")
elif model_lr.coef_[0] > 0.5 and change > 20:
    print("   📈 Наблюдается ЯВНАЯ ВОСХОДЯЩАЯ ТЕНДЕНЦИЯ")
else:
    print("   📊 Тренд НЕЯВНЫЙ или ОТСУТСТВУЕТ. Колебания носят случайный характер.")




    

Вариант 2 — Git через сетевую шару (SMB)
Если SSH — это слишком сложно, можно просто шарить папку с bare-репозиториями через обычную сетевую шару Windows.
Шаги на сервере
Создать папку C:\git_repos.
Настроить сетевую шару (Properties → Sharing).
Дать права на чтение/запись нужным пользователям.
Инициализировать bare-репозиторий как выше:
Копировать код
Powershell
cd C:\git_repos
git init --bare myproject.git
На рабочих станциях
Смонтировать шару или использовать UNC-путь:
Копировать код
Bash
git clone //SERVER_NAME/git_repos/myproject.git
или монтировать как диск:
Копировать код
Bash
net use G: \\SERVER_NAME\git_repos
git clone G:/myproject.git
⚠️ Минус: нет автоматической аутентификации Git, но для локальной сети это часто приемлемо.

# Blogicum
Blogicum - сервис ведения личных блогов.
Учебный проект с примером реализации API-функций на основе DRF 
для просмотра и создания постов.

## Используемые технологии
[Django](https://www.djangoproject.com/),
[Django REST framework](https://www.django-rest-framework.org/)

## Руководство по локальному запуску проекта
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/oleg-zharkikh/blogicum-drf
```

```
cd blogicum-drf
```
Создать и активировать виртуальное окружение;
Windows
```
python -m venv venv
source venv/Scripts/activate
```
Linux/macOS
```
python3 -m venv venv
source venv/bin/activate
```

Обновить PIP:

Windows
```
python -m pip install --upgrade pip
```
Linux/macOS
```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить проект:

Windows
```
python blogicum/manage.py runserver
```

Linux/macOS
```
python3 blogicum/manage.py runserver
```
