# China Level Telegram Bot

Telegram бот с веб-приложением для расчета стоимости доставки из Китая.

## Функциональность

- 🤖 Telegram бот с интерактивным меню
- 📱 Веб-приложение для точного расчета доставки
- 💰 Калькулятор стоимости с учетом различных параметров
- 📄 Отправка прайс-листов и документов

## Технологии

- Python 3.12
- Flask (веб-сервер)
- python-telegram-bot (Telegram API)
- HTML/CSS/JavaScript (веб-интерфейс)

## Локальная разработка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # или
   source venv/bin/activate  # Linux/Mac
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Создайте `.env` файл на основе `.env.example`
5. Запустите бота:
   ```bash
   python bot_script.py
   ```

## Деплой на Vercel

### 1. Подготовка

1. Создайте репозиторий на GitHub
2. Загрузите код в репозиторий
3. Убедитесь, что `.env` файл в `.gitignore`

### 2. Настройка Vercel

1. Зайдите на [vercel.com](https://vercel.com)
2. Подключите ваш GitHub репозиторий
3. В настройках проекта добавьте переменные окружения:
   - `BOT_TOKEN` - токен вашего Telegram бота

### 3. Получение HTTPS URL

После деплоя Vercel предоставит HTTPS URL вида:
`https://your-project-name.vercel.app`

Этот URL нужно использовать в коде бота для веб-приложения.

## Структура проекта

```
├── bot_script.py          # Основной файл бота и Flask сервера
├── index.html            # Веб-интерфейс калькулятора
├── delivery_price.xlsx   # Прайс-лист доставки
├── privileges.pdf        # Документ с бонусами
├── requirements.txt      # Python зависимости
├── vercel.json          # Конфигурация Vercel
├── .env.example          # Пример переменных окружения
├── .gitignore           # Исключения для Git
└── README.md            # Документация
```

## Настройка веб-приложения

После деплоя на Vercel:

1. Получите HTTPS URL вашего проекта
2. Обновите URL в `bot_script.py` (строка 261):
   ```python
   webapp_url = 'https://your-project-name.vercel.app/'
   ```

## Переменные окружения

- `BOT_TOKEN` - токен Telegram бота (обязательно)

## Поддержка

При возникновении проблем проверьте:
- Правильность токена бота
- Наличие всех файлов в репозитории
- Настройки переменных окружения на Vercel
