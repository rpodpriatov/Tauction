import os
import logging
from telegram import Update
from telegram.ext import (Application, CommandHandler, PreCheckoutQueryHandler,
                          MessageHandler, filters)
from telegram.error import BadRequest
from models import User, Auction
from db import db_session
from datetime import datetime
from yookassa import Configuration, Payment

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# YooMoney API Configuration
YOOMONEY_SHOP_ID = os.environ.get('YOOMONEY_SHOP_ID')
YOOMONEY_SECRET_KEY = os.environ.get('YOOMONEY_SECRET_KEY')
YOOMONEY_SHOP_ARTICLE_ID = os.environ.get('YOOMONEY_SHOP_ARTICLE_ID')

Configuration.account_id = YOOMONEY_SHOP_ID
Configuration.secret_key = YOOMONEY_SECRET_KEY

application = None  # Global variable for the bot

async def start(update: Update, context):
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text(
        'Welcome to the Auction Platform Bot! Use /buy_stars_yoomoney to purchase XTR stars.'
    )

async def buy_stars_yoomoney(update: Update, context):
    logger.info(f"buy_stars_yoomoney function called by user {update.effective_user.id}")
    try:
        # Step 1: Check if all required environment variables are set
        logger.info("Checking YooMoney configuration")
        if not all([YOOMONEY_SHOP_ID, YOOMONEY_SECRET_KEY, YOOMONEY_SHOP_ARTICLE_ID]):
            missing_vars = [var for var in ['YOOMONEY_SHOP_ID', 'YOOMONEY_SECRET_KEY', 'YOOMONEY_SHOP_ARTICLE_ID'] if not os.environ.get(var)]
            logger.error(f"YooMoney configuration is incomplete. Missing variables: {', '.join(missing_vars)}")
            await update.message.reply_text("Sorry, YooMoney payments are not available at the moment. Please try again later or contact support.")
            return

        # Step 2: Get or create user
        logger.info("Getting or creating user")
        user_id = update.effective_user.id
        user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
        if not user:
            logger.info(f"Creating new user for Telegram ID: {user_id}")
            user = User(telegram_id=str(user_id),
                        username=update.effective_user.username or 'Unknown',
                        xtr_balance=0)
            db_session.add(user)
            db_session.commit()
            logger.info(f"Created new user: {user.id}")
        else:
            logger.info(f"Found existing user: {user.id}")

        # Step 3: Parse and validate amount
        logger.info("Parsing and validating amount")
        min_amount = 10
        amount = context.args[0] if context.args else str(min_amount)
        try:
            amount = int(amount)
            if amount < min_amount:
                logger.warning(f"User {user_id} attempted to purchase less than the minimum amount")
                await update.message.reply_text(f"Minimum purchase amount is {min_amount} XTR. Please try again with a larger amount.")
                return
        except ValueError:
            logger.warning(f"User {user_id} provided an invalid amount: {amount}")
            await update.message.reply_text("Please provide a valid number of XTR to purchase. For example: /buy_stars_yoomoney 15")
            return

        # Step 4: Prepare payment data
        logger.info(f"Preparing payment data for {amount} XTR")
        total_amount = amount * 10  # 1 XTR = 10 RUB
        
        payment = Payment.create({
            "amount": {
                "value": f"{total_amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{os.getenv('BASE_URL', 'https://your-domain.com')}/yoomoney_success"
            },
            "capture": True,
            "description": f"Purchase of {amount} XTR stars for user {user.id}",
            "metadata": {
                "user_id": user.id,
                "amount": amount
            },
            "receipt": {
                "customer": {
                    "full_name": update.effective_user.full_name,
                    "phone": "",
                    "email": ""
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
        })

        logger.info(f"YooMoney payment created for user {user.id}: {payment.id}")
        confirmation_url = payment.confirmation.confirmation_url
        if confirmation_url:
            success_message = f"Please complete your payment of {amount} XTR ({total_amount} RUB) by clicking the link below:\n{confirmation_url}"
            await update.message.reply_text(success_message)
        else:
            logger.error(f"Failed to create YooMoney payment: {payment.status}")
            error_message = f"Sorry, there was an error processing your payment. Please try again later or contact support."
            await update.message.reply_text(error_message)

    except Exception as e:
        logger.error(f"Unexpected error in buy_stars_yoomoney function: {str(e)}", exc_info=True)
        error_message = "An unexpected error occurred. Please try again later or contact support."
        await update.message.reply_text(error_message)

async def pre_checkout_callback(update: Update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context):
    user_id = update.effective_user.id
    amount = update.message.successful_payment.total_amount // 100  # Convert cents to rubles

    user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
    if user:
        user.xtr_balance += amount
        db_session.commit()
        await update.message.reply_text(
            f'Thank you for your payment! {amount} XTR stars have been added to your balance.'
        )
    else:
        new_user = User(telegram_id=str(user_id),
                        username=update.effective_user.username,
                        xtr_balance=amount)
        db_session.add(new_user)
        db_session.commit()
        await update.message.reply_text(
            f'Thank you for your payment! A new account has been created for you with {amount} XTR stars.'
        )

def setup_bot() -> Application:
    global application
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error(
            "TELEGRAM_BOT_TOKEN is not set in the environment variables")
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is not set in the environment variables")

    logger.info(
        f"Setting up bot with token: {bot_token[:5]}...{bot_token[-5:]}")

    application = Application.builder().token(bot_token).build()

    logger.info("Adding command handlers")
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('buy_stars_yoomoney', buy_stars_yoomoney))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT,
                       successful_payment_callback))

    logger.info("Bot setup completed")
    return application

async def send_notification(user_id: int, message: str):
    if application:
        try:
            await application.bot.send_message(chat_id=int(user_id),
                                               text=message)
            logger.info(f"Notification sent to user {user_id}")
        except BadRequest as e:
            logger.error(
                f"BadRequest when sending notification to user {user_id}: {str(e)}"
            )
        except Exception as e:
            logger.error(
                f"Error sending notification to user {user_id}: {str(e)}")
    else:
        logger.error("Telegram application is not initialized.")
