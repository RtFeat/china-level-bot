# Инструкция по деплою на GitHub и Vercel

## Шаг 1: Подготовка проекта

Ваш проект уже подготовлен для деплоя. Структура файлов:

```
├── bot_script.py          # Основной файл бота
├── api/
│   └── index.py          # Точка входа для Vercel
├── templates/
│   └── index.html        # Веб-интерфейс
├── requirements.txt      # Python зависимости
├── vercel.json           # Конфигурация Vercel
├── .gitignore           # Исключения для Git
├── env.example          # Пример переменных окружения
└── README.md            # Документация
```

## Шаг 2: Создание GitHub репозитория

1. Зайдите на [github.com](https://github.com)
2. Нажмите "New repository"
3. Назовите репозиторий (например: `china-level-bot`)
4. Создайте репозиторий

## Шаг 3: Загрузка кода на GitHub

Выполните команды в терминале:

```bash
# Инициализация Git (если еще не сделано)
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: China Level Telegram Bot"

# Подключение к GitHub репозиторию
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Загрузка на GitHub
git push -u origin main
```

## Шаг 4: Деплой на Vercel

1. Зайдите на [vercel.com](https://vercel.com)
2. Нажмите "New Project"
3. Подключите ваш GitHub репозиторий
4. Vercel автоматически определит настройки из `vercel.json`

## Шаг 5: Настройка переменных окружения

В панели Vercel:

1. Перейдите в Settings → Environment Variables
2. Добавьте переменную:
   - **Name**: `BOT_TOKEN`
   - **Value**: ваш токен Telegram бота
   - **Environment**: Production

## Шаг 6: Обновление URL в коде

После деплоя получите URL вашего проекта (например: `https://your-project.vercel.app`)

Обновите в `bot_script.py` строку 262:

```python
webapp_url = 'https://your-project.vercel.app/'
```

И перезагрузите код на GitHub.

## Шаг 7: Проверка работы

1. Откройте ваш бот в Telegram
2. Нажмите "Точный расчет"
3. Должен открыться веб-интерфейс с HTTPS

## Важные моменты

### Что НЕ заливать на GitHub:
- `.env` файл (уже в .gitignore)
- `venv/` папку (уже в .gitignore)
- Временные файлы

### Переменные окружения на Vercel:
- `BOT_TOKEN` - токен вашего бота (обязательно)

### Если что-то не работает:
1. Проверьте логи в панели Vercel
2. Убедитесь, что токен бота правильный
3. Проверьте, что все файлы загружены на GitHub

## Структура после деплоя

После успешного деплоя у вас будет:
- ✅ HTTPS URL для веб-приложения
- ✅ Работающий Telegram бот
- ✅ Калькулятор доставки
- ✅ Автоматические обновления при изменении кода
