from quart import Quart, jsonify, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import aiohttp
import json

# Настройки
API_TOKEN = "Darnv1Egr15xSPmXWbDt2UTcVZB7bCnz"
TELEGRAM_BOT_TOKEN = "8118583051:AAGNX80Ni-NYw-98ea8F6HLGyj-73fNldfg"
WHITE_LIST = [310062211]  # Белый список пользователей

# Создаём Quart-приложение
app = Quart(__name__)

# Функция для проверки валидности IMEI
def is_valid_imei(imei: str) -> bool:
    if len(imei) != 15 or not imei.isdigit():
        return False
    total = 0
    for i, char in enumerate(imei):
        digit = int(char)
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit = digit - 9
        total += digit
    return total % 10 == 0

# Асинхронная функция для проверки IMEI через внешний сервис
async def check_imei_via_api(imei):
    if not imei or not isinstance(imei, str):
        return {"error": "Invalid deviceId"}

    url = "https://api.imeicheck.net/v1/checks"
    headers = {
        'Authorization': 'Bearer g7UIzVuMnwSrFPFZfcIX63s6Cr00msA3loFn2gggfa1a27b9',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
        }
    payload = json.dumps({
        "deviceId": imei,  
        "serviceId": 12
        })

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            if response.status == 201:
                return await response.json()
            else:
                return {"error": "Failed to check IMEI", "status_code": response.status}

# Маршрут для проверки IMEI через API
@app.route("/api/check-imei", methods=["POST"])
async def check_imei():
    data = await request.json
    imei = data.get("imei")
    token = data.get("token")
    
    # Проверка токена
    if not token or token not in {API_TOKEN}:
        return jsonify({"error": "Unauthorized"}), 401

    # Проверка наличия IMEI
    if not imei:
        return jsonify({"error": "IMEI is required"}), 400

    # Проверка IMEI через внешний сервис
    result = await check_imei_via_api(imei)
    return jsonify(result)

# Команда /start для Telegram-бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in WHITE_LIST:
        await update.message.reply_text("Доступ разрешён! Отправьте IMEI для проверки.")
    else:
        await update.message.reply_text("Доступ запрещён. Ваш ID не в белом списке.")

# Обработка IMEI для Telegram-бота
async def handle_imei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in WHITE_LIST:
        await update.message.reply_text("Доступ запрещён.")
        return

    imei = update.message.text

    # Проверка валидности IMEI
    if not is_valid_imei(imei):
        await update.message.reply_text("Некорректный IMEI. Пожалуйста, введите 15-значный IMEI.")
        return
    
    # Отправка запроса к API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:5000/api/check-imei",
                json={"imei": imei, "token": API_TOKEN}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    await update.message.reply_text(f"Результат проверки: {result}")
                else:
                    await update.message.reply_text("Ошибка при проверке IMEI.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Запуск Telegram-бота
async def run_bot():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_imei))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

# Основная функция для запуска Quart и бота
async def main():
    await asyncio.gather(
        app.run_task(host="127.0.0.1", port=5000),  # Запуск Quart
        run_bot()  # Запуск Telegram-бота
    )

# Запуск приложения
if __name__ == "__main__":
    asyncio.run(main())