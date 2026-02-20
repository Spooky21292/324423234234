"""
Самый простой Telegram-бот с командой /weather.

Что делает:
1) Работает через библиотеку python-telegram-bot.
2) Отвечает в группах на команду /weather.
3) Берёт погоду для города Старый Оскол из OpenWeatherMap.

Перед запуском установите переменные окружения:
- TELEGRAM_BOT_TOKEN: токен вашего Telegram-бота
- OPENWEATHER_API_KEY: API-ключ OpenWeatherMap
"""

import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


# Город, для которого запрашиваем погоду
CITY = "Старый Оскол"
# Бесплатный endpoint текущей погоды OpenWeatherMap
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /weather."""
    api_key = os.getenv("OPENWEATHER_API_KEY")

    # Если ключ не задан, сразу сообщаем об ошибке
    if not api_key:
        await update.message.reply_text(
            "Не задан OPENWEATHER_API_KEY. Добавьте ключ OpenWeatherMap в переменные окружения."
        )
        return

    # Параметры запроса:
    # q - город, appid - ключ API, units=metric - температура в °C, lang=ru - описание на русском
    params = {
        "q": CITY,
        "appid": api_key,
        "units": "metric",
        "lang": "ru",
    }

    try:
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Достаём нужные поля из ответа API
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]

        text = (
            f"Погода в городе {CITY}:\n"
            f"{description.capitalize()}\n"
            f"Температура: {temp:.1f}°C\n"
            f"Ощущается как: {feels_like:.1f}°C"
        )
        await update.message.reply_text(text)

    except requests.RequestException:
        # Ошибка сети или ответа API
        await update.message.reply_text("Не удалось получить погоду. Попробуйте позже.")
    except (KeyError, IndexError, TypeError, ValueError):
        # Если API вернул неожиданный формат данных
        await update.message.reply_text("Сервис погоды вернул неожиданный ответ.")


def main() -> None:
    """Запуск бота."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")

    # Создаём приложение Telegram-бота
    application = Application.builder().token(token).build()

    # Регистрируем команду /weather
    application.add_handler(CommandHandler("weather", weather))

    # Разрешаем боту получать сообщения в группах (по умолчанию это работает,
    # важно только отключить Privacy Mode у бота через BotFather, если нужно читать
    # обычные сообщения. Для команд /weather обычно достаточно стандартных настроек)
    application.run_polling()


if __name__ == "__main__":
    main()
