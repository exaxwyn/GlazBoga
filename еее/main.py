import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота
TOKEN = '7504155571:7_YSODM'
# Пример адреса для криптовалютных платежей (нужно заменить на реальный)
CRYPTO_WALLET_ADDRESS = '4356веаанпмо'

# Подключение к базе данных SQLite
def db_connect():
    conn = sqlite3.connect('bot_database.db')
    return conn

def setup_database():
    conn = db_connect()
    cursor = conn.cursor()
    # Создание таблиц
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

setup_database()

def get_user_balance(user_id: int) -> int:
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_user_balance(user_id: int, amount: int):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, balance)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?
    ''', (user_id, amount, amount))
    conn.commit()
    conn.close()

def add_transaction(user_id: int, amount: int):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO transactions (user_id, amount) VALUES (?, ?)', (user_id, amount))
    conn.commit()
    conn.close()

# Функция для старта работы
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я ваш помощник по поиску информации. Используйте /help для получения списка команд.')

# Функция для получения справки
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
    /start - Начало работы
    /help - Получить список команд
    /subscribe - Подписка на использование бота
    /balance - Проверка текущего баланса
    /topup - Пополнение баланса
    /searchinfo - Поиск информации о гражданине
    /addressinfo - Информация о месте проживания
    /carowner - Информация о владельце автотранспорта
    /phoneinfo - Информация о владельце номера мобильного телефона
    /socialprofile - Поиск привязанного номера телефона по ссылке на соцсеть
    /imageinfo - Поиск по фото
    /passportinfo - Информация по паспорту
    /emailinfo - Поиск информации по электронной почте
    /criminalinfo - Информация о криминальном прошлом
    /propertyinfo - Информация из Росреестра
    /privacy - Защита ваших личных данных
    """
    await update.message.reply_text(help_text)

# Функция для проверки и пополнения баланса
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    balance = get_user_balance(user_id)
    await update.message.reply_text(f"Ваш текущий баланс: {balance} рублей.")

async def topup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Чтобы пополнить баланс, отправьте криптовалюту на следующий адрес:\n\n{CRYPTO_WALLET_ADDRESS}\n\n"
        "После выполнения платежа, сообщите нам о транзакции, чтобы мы могли обновить ваш баланс."
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    update_user_balance(user_id, 0)  # Создание записи пользователя с нулевым балансом
    await update.message.reply_text("Ваша подписка активирована. Пополните баланс с помощью команды /topup.")

# Функция для обработки платежей
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Эта функция должна быть вызвана, когда получен платеж
    # Пример получения платежа
    amount = 100  # Это пример, реальная сумма должна быть получена из транзакции
    update_user_balance(user_id, amount)
    add_transaction(user_id, amount)
    await update.message.reply_text(f"Ваш баланс пополнен на {amount} рублей. Текущий баланс: {get_user_balance(user_id)} рублей.")

# Реальные функции поиска информации
async def search_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска информации
    # Например, сделаем запрос к API и вернем результат
    response = requests.get(f'https://api.example.com/searchinfo?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Информация о гражданине: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def address_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска информации о месте проживания
    response = requests.get(f'https://api.example.com/addressinfo?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Информация о месте проживания: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def car_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска информации о владельце автотранспорта
    response = requests.get(f'https://api.example.com/carowner?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Информация о владельце автотранспорта: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def phone_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска информации о владельце номера мобильного телефона
    response = requests.get(f'https://api.example.com/phoneinfo?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Информация о владельце номера мобильного телефона: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def social_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска привязанного номера телефона по ссылке на соцсеть
    response = requests.get(f'https://api.example.com/socialprofile?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Привязанный номер телефона по ссылке на соцсеть: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def image_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска по фото
    response = requests.get(f'https://api.example.com/imageinfo?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Поиск по фото выполнен: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def passport_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска по паспорту
    response = requests.get(f'https://api.example.com/passportinfo?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Информация по паспорту: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def email_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска по электронной почте
    response = requests.get(f'https://api.example.com/emailinfo?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Информация по электронной почте: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def criminal_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска информации о криминальном прошлом
    response = requests.get(f'https://api.example.com/criminalinfo?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Информация о криминальном прошлом: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def property_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику поиска информации из Росреестра
    response = requests.get(f'https://api.example.com/propertyinfo?user_id={user_id}')
    if response.status_code == 200:
        data = response.json()
        result = f"Информация из Росреестра: {data}"
    else:
        result = "Не удалось получить информацию. Попробуйте позже."
    await update.message.reply_text(result)

async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Реализуйте логику защиты личных данных
    response = requests.post(f'https://api.example.com/privacy', json={'user_id': user_id})
    if response.status_code == 200:
        data = response.json()
        result = f"Личные данные защищены: {data}"
    else:
        result = "Не удалось защитить данные. Попробуйте позже."
    await update.message.reply_text(result)

def main():
    # Создание и запуск бота
    application = Application.builder().token(TOKEN).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('balance', balance))
    application.add_handler(CommandHandler('topup', topup))
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(CommandHandler('searchinfo', search_info))
    application.add_handler(CommandHandler('addressinfo', address_info))
    application.add_handler(CommandHandler('carowner', car_owner))
    application.add_handler(CommandHandler('phoneinfo', phone_info))
    application.add_handler(CommandHandler('socialprofile', social_profile))
    application.add_handler(CommandHandler('imageinfo', image_info))
    application.add_handler(CommandHandler('passportinfo', passport_info))
    application.add_handler(CommandHandler('emailinfo', email_info))
    application.add_handler(CommandHandler('criminalinfo', criminal_info))
    application.add_handler(CommandHandler('propertyinfo', property_info))
    application.add_handler(CommandHandler('privacy', privacy))

    # Добавление обработчика для пополнения баланса и обработки платежей
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment))

    application.run_polling()

if __name__ == '__main__':
    main()
