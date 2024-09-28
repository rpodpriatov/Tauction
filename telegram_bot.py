import os
import logging
import re
import time
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext
)
from telegram.error import BadRequest
from models import User, Auction
from db import db_session
from datetime import datetime
from yookassa import Configuration, Payment

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация YooMoney API
YOOMONEY_SHOP_ID = os.environ.get('YOOMONEY_SHOP_ID')
YOOMONEY_SECRET_KEY = os.environ.get('YOOMONEY_SECRET_KEY')
YOOMONEY_SHOP_ARTICLE_ID = os.environ.get('YOOMONEY_SHOP_ARTICLE_ID')

Configuration.account_id = YOOMONEY_SHOP_ID
Configuration.secret_key = YOOMONEY_SECRET_KEY

application = None  # Глобальная переменная для бота

# Определение состояний для ConversationHandler
AWAITING_EMAIL = 1

# Helper function to handle YooMoney API errors
def handle_yoomoney_error(response):
    error_data = response.json()
    logger.error(f"YooMoney API error: {error_data.get('description')} (Code: {error_data.get('code')})")
    if 'parameter' in error_data:
        logger.error(f"Error parameter: {error_data['parameter']}")
    return error_data.get('description')

# Обработчик команды /start
async def start(update: Update, context):
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text(
        'Welcome to the Auction Platform Bot! Use /buy_stars_yoomoney to purchase XTR stars.'
    )

# Обработчик команды /buy_stars_yoomoney
async def buy_stars_yoomoney(update: Update, context: CallbackContext):
    logger.info(f"buy_stars_yoomoney function called by user {update.effective_user.id}")
    try:
        # Шаг 1: Проверка настроек YooMoney
        if not all([YOOMONEY_SHOP_ID, YOOMONEY_SECRET_KEY, YOOMONEY_SHOP_ARTICLE_ID]):
            missing_vars = [var for var in ['YOOMONEY_SHOP_ID', 'YOOMONEY_SECRET_KEY', 'YOOMONEY_SHOP_ARTICLE_ID'] if not os.environ.get(var)]
            logger.error(f"YooMoney configuration is incomplete. Missing variables: {', '.join(missing_vars)}")
            await update.message.reply_text("Sorry, YooMoney payments are not available at the moment. Please try again later or contact support.")
            return ConversationHandler.END

        # Шаг 2: Получение или создание пользователя
        user_id = update.effective_user.id
        user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
        if not user:
            logger.info(f"Creating new user for Telegram ID: {user_id}")
            user = User(
                telegram_id=str(user_id),
                username=update.effective_user.username or 'Unknown',
                xtr_balance=0
            )
            db_session.add(user)
            db_session.commit()
            logger.info(f"Created new user: {user.id}")
        else:
            logger.info(f"Found existing user: {user.id}")

        # Шаг 3: Парсинг и валидация суммы
        min_amount = 10
        amount = context.args[0] if context.args else str(min_amount)
        try:
            amount = int(amount)
            if amount < min_amount:
                logger.warning(f"User {user_id} attempted to purchase less than the minimum amount")
                await update.message.reply_text(f"Minimum purchase amount is {min_amount} XTR. Please try again with a larger amount.")
                return ConversationHandler.END
        except ValueError:
            logger.warning(f"User {user_id} provided an invalid amount: {amount}")
            await update.message.reply_text("Please provide a valid number of XTR to purchase. For example: /buy_stars_yoomoney 15")
            return ConversationHandler.END

        # Сохраняем сумму в контексте пользователя
        context.user_data['amount'] = amount

        # Запрашиваем email адрес
        await update.message.reply_text("Please enter your email address to proceed with the payment:")
        return AWAITING_EMAIL

    except Exception as e:
        logger.error(f"Unexpected error in buy_stars_yoomoney function: {str(e)}", exc_info=True)
        error_message = "An unexpected error occurred. Please try again later or contact support."
        await update.message.reply_text(error_message)
        return ConversationHandler.END

async def process_email(update: Update, context: CallbackContext):
    email = update.message.text
    user_id = update.effective_user.id
    amount = context.user_data.get('amount')

    # Валидация email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await update.message.reply_text("Invalid email format. Please provide a valid email address.")
        return AWAITING_EMAIL

    try:
        # Сохраняем email в базе данных
        user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
        if user:
            user.email = email
            db_session.commit()

        # Создаем платеж
        await create_yoomoney_payment(update, context, email)
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Unexpected error in process_email function: {str(e)}", exc_info=True)
        error_message = "An unexpected error occurred. Please try again later or contact support."
        await update.message.reply_text(error_message)
        return ConversationHandler.END

async def create_yoomoney_payment(update: Update, context, email):
    user_id = update.effective_user.id
    amount = context.user_data.get('amount')
    
    # Подготовка данных платежа
    total_amount = amount * 10  # 1 XTR = 10 RUB
    
    payment_data = {
        "amount": {
            "value": f"{total_amount:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"{os.getenv('BASE_URL', 'https://your-domain.com')}/yoomoney_success"
        },
        "capture": True,
        "description": f"Purchase of {amount} XTR stars for user {user_id}",
        "metadata": {
            "user_id": user_id,
            "amount": amount
        },
        "receipt": {
            "customer": {
                "full_name": update.effective_user.full_name,
                "email": email
            },
            "items": [
                {
                    "description": "XTR Stars",
                    "quantity": "1",
                    "amount": {
                        "value": f"{total_amount:.2f}",
                        "currency": "RUB"
                    },
                    "vat_code": "1",
                    "payment_mode": "full_prepayment",
                    "payment_subject": "service"
                }
            ]
        }
    }

    if YOOMONEY_SHOP_ARTICLE_ID:
        payment_data["merchant_article_id"] = YOOMONEY_SHOP_ARTICLE_ID

    logger.info(f"Payment data prepared: {payment_data}")
    logger.info(f"Email used for payment (masked): {email[:3]}...{email[-3:]}")

    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            response = Payment.create(payment_data)
            
            if isinstance(response, Payment) and response.status == 'pending':
                logger.info(f"YooMoney payment created for user {user_id}: {response.id}")
                confirmation_url = response.confirmation.confirmation_url
                if confirmation_url:
                    success_message = f"Please complete your payment of {amount} XTR ({total_amount} RUB) by clicking the link below:\n{confirmation_url}"
                    await update.message.reply_text(success_message)
                    return
                else:
                    logger.error(f"Failed to create YooMoney payment: {response.status}")
                    error_message = "Sorry, there was an error processing your payment. Please try again later or contact support."
                    await update.message.reply_text(error_message)
                    return
            else:
                error_description = handle_yoomoney_error(response)
                if response.status_code == 400:
                    logger.error(f"Invalid request: {error_description}")
                    await update.message.reply_text(f"Invalid request: {error_description}. Please try again or contact support.")
                elif response.status_code == 401:
                    logger.error("Authentication failed. Check YooMoney credentials.")
                    await update.message.reply_text("Payment system authentication error. Please contact support.")
                elif response.status_code == 403:
                    logger.error(f"Permission denied: {error_description}")
                    await update.message.reply_text("Permission denied for this operation. Please contact support.")
                elif response.status_code == 429:
                    logger.warning("Too many requests. Implementing exponential backoff.")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * retry_delay
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        await update.message.reply_text("The payment system is currently overloaded. Please try again later.")
                elif response.status_code == 500:
                    logger.error(f"YooMoney server error: {error_description}")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * retry_delay
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        await update.message.reply_text("The payment system is currently experiencing issues. Please try again later.")
                else:
                    logger.error(f"Unexpected error: {error_description}")
                    await update.message.reply_text(f"An unexpected error occurred: {error_description}. Please try again later or contact support.")
                return

        except Exception as e:
            logger.error(f"Exception in create_yoomoney_payment: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * retry_delay
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                await update.message.reply_text("An unexpected error occurred while processing your payment. Please try again later or contact support.")
                return

# Обработчик предоплаты
async def pre_checkout_callback(update: Update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

# Обработчик успешной оплаты
async def successful_payment_callback(update: Update, context):
    user_id = update.effective_user.id
    amount = update.message.successful_payment.total_amount // 100  # Конвертация копеек в рубли

    user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
    if user:
        user.xtr_balance += amount
        db_session.commit()
        await update.message.reply_text(
            f'Thank you for your payment! {amount} XTR stars have been added to your balance.'
        )
    else:
        new_user = User(
            telegram_id=str(user_id),
            username=update.effective_user.username,
            xtr_balance=amount
        )
        db_session.add(new_user)
        db_session.commit()
        await update.message.reply_text(
            f'Thank you for your payment! A new account has been created for you with {amount} XTR stars.'
        )

# Настройка бота
def setup_bot() -> Application:
    global application
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in the environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment variables")

    logger.info(f"Setting up bot with token: {bot_token[:5]}...{bot_token[-5:]}")

    application = Application.builder().token(bot_token).build()

    logger.info("Adding command handlers")
    
    # Создаем ConversationHandler для команды buy_stars_yoomoney
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('buy_stars_yoomoney', buy_stars_yoomoney)],
        states={
            AWAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_email)]
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)]
    )
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT,
                       successful_payment_callback))

    logger.info("Bot setup completed")
    return application

# Функция для отправки уведомлений
async def send_notification(user_id: int, message: str):
    logger.info(f"send_notification called with user_id={user_id}, message={message}")
    if application:
        try:
            await application.bot.send_message(chat_id=int(user_id), text=message)
            logger.info(f"Notification sent to user {user_id}")
        except BadRequest as e:
            logger.error(
                f"BadRequest when sending notification to user {user_id}: {str(e)}"
            )
        except Exception as e:
            logger.error(
                f"Error sending notification to user {user_id}: {str(e)}"
            )
    else:
        logger.error("Telegram application is not initialized.")
