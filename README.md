Детализированная Архитектура Приложения “Бот-Аукцион” с Интеграцией USDC

Содержание

    1.	Обзор
    2.	Компоненты Архитектуры
    •	2.1. Веб-приложение (Flask)
    •	2.2. Telegram-бот
    •	2.3. База данных
    •	2.4. Платежный Провайдер и Интеграция USDC
    •	2.5. Эскроу-система
    •	2.6. Система Разрешения Споров
    3.	Модели Данных и База Данных
    •	3.1. Схема Базы Данных
    •	3.2. Модели Данных
    •	3.2.1. Пользователь (User)
    •	3.2.2. Кошелек (Wallet)
    •	3.2.3. Транзакция (Transaction)
    •	3.2.4. Аукцион (Auction)
    •	3.2.5. Ставка (Bid)
    •	3.2.6. Заказ (Order)
    •	3.2.7. Сообщение (Message)
    •	3.2.8. Спор (Dispute)
    •	3.2.9. Отзыв (Review)
    4.	Функциональные Компоненты и Примеры Функций
    •	4.1. Регистрация и Аутентификация
    •	4.2. Верификация Пользователя (KYC)
    •	4.3. Управление Балансом USDC
    •	4.3.1. Пополнение Баланса (Депозит)
    •	4.3.2. Вывод Средств
    •	4.4. Создание и Управление Аукционами
    •	4.5. Участие в Аукционах и Ставки
    •	4.6. Завершение Аукциона и Создание Заказа
    •	4.7. Передача Товара/Услуги
    •	4.8. Разрешение Споров
    5.	Интеграция с Платежным Провайдером
    •	5.1. Техническая Интеграция
    •	5.2. Примеры Реализации
    6.	Меры Безопасности и Предотвращение Мошенничества
    •	6.1. Технические Меры
    •	6.2. Организационные Меры
    7.	Технологии и Инструменты
    8.	Структура Проекта
    9.	Развертывание и Запуск Приложения
    10.	Диаграммы
    •	10.1. Диаграмма Вариантов Использования (Use Case Diagram)
    •	10.2. Диаграмма Классов (Class Diagram)
    •	10.3. Диаграмма Объектов (Object Diagram)
    •	10.4. Диаграммы Последовательности (Sequence Diagrams)
    •	10.5. Диаграммы Деятельности (Activity Diagrams)
    •	10.6. Диаграмма Компонентов (Component Diagram)
    •	10.7. Диаграмма Развертывания (Deployment Diagram)
    •	10.8. Диаграммы Состояний (State Diagrams)
    •	10.9. Диаграмма Времени (Timing Diagram)
    11.	Заключение



1. Обзор

Приложение “Бот-Аукцион” представляет собой веб-платформу и Telegram-бота, объединенных для проведения онлайн-аукционов с использованием криптовалюты USDC. Пользователи могут регистрироваться, проходить верификацию (KYC), управлять своим балансом USDC, создавать и участвовать в аукционах, а также обмениваться товарами и услугами с использованием безопасной эскроу-системы.



2. Компоненты Архитектуры



2.1. Веб-приложение (Flask)

Назначение: Основной интерфейс для пользователей, предоставляющий функциональность платформы.

Функциональность:

    •	Регистрация и аутентификация пользователей.
    •	Верификация пользователей (KYC).
    •	Управление балансом USDC (депозиты и выводы).
    •	Создание и управление аукционами.
    •	Участие в аукционах и ставки.
    •	Управление заказами и эскроу-система.
    •	Система разрешения споров.
    •	Обмен сообщениями между пользователями.
    •	Управление профилем и настройками.



2.2. Telegram-бот

Назначение: Предоставление уведомлений и дополнительного взаимодействия с пользователями.

Функциональность:

    •	Отправка уведомлений о событиях (новые ставки, завершение аукциона и т.д.).
    •	Обработка основных команд (/start, /notifications, /messages).
    •	Примечание: Финансовые операции не выполняются через бота.



2.3. База данных

Тип: PostgreSQL

Назначение: Хранение всей необходимой информации о пользователях, аукционах, транзакциях и т.д.



2.4. Платежный Провайдер и Интеграция USDC

Назначение: Обеспечение обработки платежей в USDC.

Провайдер: Coinbase Commerce (или аналогичный)

Функциональность:

    •	Генерация уникальных депозитных адресов.
    •	Отслеживание входящих транзакций через вебхуки.
    •	Обработка выводов средств через API.



2.5. Эскроу-система

Назначение: Безопасное хранение средств до завершения сделки.

Функциональность:

    •	Заморозка средств победителя аукциона.
    •	Освобождение средств продавцу после подтверждения получения товара.



2.6. Система Разрешения Споров

Назначение: Разрешение конфликтных ситуаций между пользователями.

Функциональность:

    •	Открытие спора пользователем.
    •	Модерация спора администраторами.
    •	Принятие решения и соответствующее распределение средств.



3. Модели Данных и База Данных



3.1. Схема Базы Данных

Схема базы данных включает основные таблицы и связи между ними:

    •	users
    •	wallets
    •	transactions
    •	auctions
    •	bids
    •	orders
    •	messages
    •	disputes
    •	reviews

Связи между таблицами:

    •	Один пользователь имеет один кошелек.
    •	Пользователь может создавать несколько аукционов и делать ставки на разные аукционы.
    •	Аукцион имеет множество ставок и одного победителя.
    •	Заказ связывает покупателя и продавца после завершения аукциона.
    •	Сообщения связывают отправителя и получателя.
    •	Спор связан с заказом и инициатором.



3.2. Модели Данных



3.2.1. Пользователь (User)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(64), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    username = db.Column(db.String(64), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    kyc_status = db.Column(db.String(20), default='pending')  # 'pending', 'verified', 'rejected'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet = db.relationship('Wallet', backref='user', uselist=False)
    auctions = db.relationship('Auction', backref='seller', lazy='dynamic')
    bids = db.relationship('Bid', backref='bidder', lazy='dynamic')
    orders = db.relationship('Order', backref='buyer', foreign_keys='Order.buyer_id', lazy='dynamic')
    messages_sent = db.relationship('Message', backref='sender', foreign_keys='Message.sender_id', lazy='dynamic')
    messages_received = db.relationship('Message', backref='recipient', foreign_keys='Message.recipient_id', lazy='dynamic')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')



3.2.2. Кошелек (Wallet)

class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    balance_usdc = db.Column(db.Numeric(precision=18, scale=8), default=0)
    deposit_address = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='wallet', lazy='dynamic')



3.2.3. Транзакция (Transaction)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'))
    type = db.Column(db.String(20))  # 'deposit', 'withdrawal', 'escrow_hold', 'escrow_release'
    amount_usdc = db.Column(db.Numeric(precision=18, scale=8))
    status = db.Column(db.String(20))  # 'pending', 'confirmed', 'failed'
    transaction_hash = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



3.2.4. Аукцион (Auction)

class Auction(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(255))
    starting_price = db.Column(db.Numeric(precision=18, scale=8))
    current_price = db.Column(db.Numeric(precision=18, scale=8))
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    auction_type = db.Column(db.String(50))  # 'english', 'dutch', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bids = db.relationship('Bid', backref='auction', lazy='dynamic')
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    order = db.relationship('Order', backref='auction', uselist=False)



3.2.5. Ставка (Bid)

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'))
    bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Numeric(precision=18, scale=8))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



3.2.6. Заказ (Order)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20))  # 'pending', 'shipped', 'delivered', 'completed', 'disputed'
    shipping_address = db.Column(db.Text)
    tracking_number = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    dispute = db.relationship('Dispute', backref='order', uselist=False)



3.2.7. Сообщение (Message)

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



3.2.8. Спор (Dispute)

class Dispute(db.Model):
    __tablename__ = 'disputes'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reason = db.Column(db.Text)
    status = db.Column(db.String(20))  # 'open', 'under_review', 'resolved'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    initiator = db.relationship('User', backref='initiated_disputes', foreign_keys=[initiator_id])



3.2.9. Отзыв (Review)

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviewed_user = db.relationship('User', backref='reviews_received', foreign_keys=[reviewed_user_id])



4. Функциональные Компоненты и Примеры Функций



4.1. Регистрация и Аутентификация

Маршруты и Функции:

    •	Регистрация (/register):

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

    •	Аутентификация (/login):

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)



4.2. Верификация Пользователя (KYC)

Маршрут и Функция:

    •	Загрузка Документов KYC (/kyc):

@app.route('/kyc', methods=['GET', 'POST'])
@login_required
def kyc():
    form = KYCForm()
    if form.validate_on_submit():
        # Сохранение загруженных документов
        document = form.document.data
        filename = secure_filename(document.filename)
        document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Обновление статуса пользователя
        current_user.kyc_status = 'pending'
        db.session.commit()

        flash('Documents uploaded successfully. Please wait for verification.', 'info')
        return redirect(url_for('dashboard'))
    return render_template('kyc.html', form=form)



4.3. Управление Балансом USDC



4.3.1. Пополнение Баланса (Депозит)

Маршрут и Функция:

    •	Пополнение Баланса (/deposit):

@app.route('/deposit', methods=['GET'])
@login_required
def deposit():
    deposit_address = current_user.wallet.deposit_address
    return render_template('deposit.html', deposit_address=deposit_address)

Обработка Вебхуков от Платежного Провайдера:

@app.route('/webhook/coinbase', methods=['POST'])
def coinbase_webhook():
    data = request.get_json()
    event = data['event']

    if event['type'] == 'charge:confirmed':
        deposit_address = event['data']['addresses']['ethereum']
        wallet = Wallet.query.filter_by(deposit_address=deposit_address).first()
        if wallet:
            amount = Decimal(event['data']['pricing']['local']['amount'])
            transaction = Transaction(
                wallet_id=wallet.id,
                type='deposit',
                amount_usdc=amount,
                status='confirmed',
                transaction_hash=event['data']['id']
            )
            wallet.balance_usdc += amount
            db.session.add(transaction)
            db.session.commit()
    return '', 200



4.3.2. Вывод Средств

Маршрут и Функция:

    •	Запрос на Вывод Средств (/withdraw):

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    form = WithdrawForm()
    if form.validate_on_submit():
        amount = form.amount.data
        address = form.address.data

        if amount > current_user.wallet.balance_usdc:
            flash('Insufficient balance.', 'danger')
        else:
            # Создание транзакции вывода
            transaction = Transaction(
                wallet_id=current_user.wallet.id,
                type='withdrawal',
                amount_usdc=amount,
                status='pending'
            )
            current_user.wallet.balance_usdc -= amount
            db.session.add(transaction)
            db.session.commit()

            # Инициирование вывода через платежный провайдер
            initiate_withdrawal(address, amount, transaction.id)

            flash('Withdrawal request submitted.', 'info')
            return redirect(url_for('balance'))
    return render_template('withdraw.html', form=form)

Функция Инициирования Вывода:

def initiate_withdrawal(address, amount, transaction_id):
    # Пример взаимодействия с платежным провайдером
    # Coinbase Commerce не поддерживает исходящие транзакции,
    # поэтому потребуется использовать другой сервис или кошелек с поддержкой API.
    pass  # Реализация зависит от выбранного провайдера



4.4. Создание и Управление Аукционами

Маршрут и Функция:

    •	Создание Аукциона (/auction/new):

@app.route('/auction/new', methods=['GET', 'POST'])
@login_required
def new_auction():
    form = AuctionForm()
    if form.validate_on_submit():
        auction = Auction(
            seller_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            starting_price=form.starting_price.data,
            current_price=form.starting_price.data,
            end_time=form.end_time.data,
            auction_type=form.auction_type.data
        )
        # Обработка изображения
        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            auction.image_filename = filename

        db.session.add(auction)
        db.session.commit()
        flash('Auction created successfully.', 'success')
        return redirect(url_for('auction_detail', auction_id=auction.id))
    return render_template('new_auction.html', form=form)



4.5. Участие в Аукционах и Ставки

Маршрут и Функция:

    •	Делание Ставки (/auction/<int:auction_id>/bid):

@app.route('/auction/<int:auction_id>/bid', methods=['POST'])
@login_required
def place_bid(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    amount = Decimal(request.form['amount'])

    if amount <= auction.current_price:
        flash('Bid amount must be higher than current price.', 'danger')
    elif amount > current_user.wallet.balance_usdc:
        flash('Insufficient balance.', 'danger')
    else:
        bid = Bid(
            auction_id=auction.id,
            bidder_id=current_user.id,
            amount=amount
        )
        auction.current_price = amount
        db.session.add(bid)
        db.session.commit()
        flash('Bid placed successfully.', 'success')
        # Отправка уведомления продавцу через Telegram-бот
        notify_user(auction.seller_id, f'New bid on your auction "{auction.title}"')
    return redirect(url_for('auction_detail', auction_id=auction.id))



4.6. Завершение Аукциона и Создание Заказа

Планировщик Задач:

    •	Использование APScheduler для проверки завершенных аукционов.

def check_auctions():
    now = datetime.utcnow()
    auctions = Auction.query.filter(Auction.end_time <= now, Auction.is_active == True).all()
    for auction in auctions:
        auction.is_active = False
        highest_bid = auction.bids.order_by(Bid.amount.desc()).first()
        if highest_bid:
            auction.winner_id = highest_bid.bidder_id
            # Заморозка средств
            escrow_hold(auction.winner_id, highest_bid.amount, auction.id)
            # Создание заказа
            order = Order(
                auction_id=auction.id,
                buyer_id=highest_bid.bidder_id,
                seller_id=auction.seller_id,
                status='pending'
            )
            db.session.add(order)
            # Уведомления
            notify_user(auction.seller_id, f'Your auction "{auction.title}" has ended. Winner: {highest_bid.bidder.username}')
            notify_user(highest_bid.bidder_id, f'You won the auction "{auction.title}". Please proceed to order details.')
        else:
            notify_user(auction.seller_id, f'Your auction "{auction.title}" has ended with no bids.')
        db.session.commit()



4.7. Передача Товара/Услуги

Маршрут и Функция:

    •	Обновление Статуса Заказа (/order/<int:order_id>/update):

@app.route('/order/<int:order_id>/update', methods=['POST'])
@login_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.id not in [order.buyer_id, order.seller_id]:
        abort(403)

    if 'tracking_number' in request.form:
        order.tracking_number = request.form['tracking_number']
        order.status = 'shipped'
        db.session.commit()
        flash('Order status updated to "shipped".', 'success')
        notify_user(order.buyer_id, f'Your order has been shipped. Tracking number: {order.tracking_number}')
    elif 'confirm_delivery' in request.form:
        order.status = 'delivered'
        # Освобождение средств из эскроу
        escrow_release(order.seller_id, order.auction.current_price, order.auction.id)
        db.session.commit()
        flash('Order marked as delivered.', 'success')
        notify_user(order.seller_id, f'Buyer confirmed delivery for order #{order.id}. Funds have been released.')
    return redirect(url_for('order_detail', order_id=order.id))



4.8. Разрешение Споров

Маршрут и Функция:

    •	Открытие Спора (/order/<int:order_id>/dispute):

@app.route('/order/<int:order_id>/dispute', methods=['GET', 'POST'])
@login_required
def open_dispute(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.id not in [order.buyer_id, order.seller_id]:
        abort(403)

    form = DisputeForm()
    if form.validate_on_submit():
        dispute = Dispute(
            order_id=order.id,
            initiator_id=current_user.id,
            reason=form.reason.data,
            status='open'
        )
        order.status = 'disputed'
        db.session.add(dispute)
        db.session.commit()
        flash('Dispute opened successfully.', 'info')
        notify_admins(f'Dispute opened for order #{order.id}.')
        return redirect(url_for('order_detail', order_id=order.id))
    return render_template('open_dispute.html', form=form, order=order)



5. Интеграция с Платежным Провайдером



5.1. Техническая Интеграция

Шаги:

    1.	Регистрация в Coinbase Commerce и получение API-ключей.
    2.	Настройка вебхуков для получения уведомлений о транзакциях.
    3.	Генерация депозитных адресов для каждого пользователя.
    4.	Использование API для обработки выводов средств.



5.2. Примеры Реализации

Создание Клиента API:

from coinbase_commerce.client import Client

coinbase_api = Client(api_key=app.config['COINBASE_COMMERCE_API_KEY'])

Генерация Депозитного Адреса:

def generate_deposit_address(user):
    charge = coinbase_api.charge.create(
        name=f'Deposit for User {user.id}',
        description='USDC Deposit',
        pricing_type='no_price',
        metadata={'user_id': user.id}
    )
    deposit_address = charge['addresses']['USDC']
    user.wallet.deposit_address = deposit_address
    db.session.commit()

Обработка Выводов:

def initiate_withdrawal(address, amount, transaction_id):
    # Пример отправки средств через платежный провайдер
    # Реализация зависит от выбранного провайдера
    pass



6. Меры Безопасности и Предотвращение Мошенничества



6.1. Технические Меры

    •	Шифрование: Использование SSL/TLS для всех соединений.
    •	Хэширование Паролей: Использование bcrypt для хэширования паролей.
    •	Двухфакторная Аутентификация: Реализация 2FA с использованием Google Authenticator.
    •	Валидация Данных: Использование CSRF-токенов и валидация форм.
    •	Мониторинг: Логирование действий пользователей и мониторинг транзакций.
    •	Ограничение Количества Запросов: Использование Flask-Limiter для предотвращения брутфорс-атак.



6.2. Организационные Меры

    •	KYC/AML: Обязательная верификация пользователей перед выполнением финансовых операций.
    •	Политики Безопасности: Разработка и публикация политик использования и конфиденциальности.
    •	Обучение Персонала: Регулярное обучение команды по вопросам безопасности.



7. Технологии и Инструменты

    •	Язык программирования: Python 3.11
    •	Веб-фреймворк: Flask
    •	База данных: PostgreSQL
    •	ORM: SQLAlchemy
    •	Аутентификация: Flask-Login, Flask-Security
    •	Формы и Валидация: Flask-WTF
    •	Планировщик Задач: APScheduler
    •	Telegram-бот: python-telegram-bot
    •	Платежный Провайдер: Coinbase Commerce API
    •	Логирование: Python logging, Sentry
    •	Контейнеризация: Docker
    •	Тестирование: pytest
    •	Управление Зависимостями: pip, requirements.txt



8. Структура Проекта

your_project/
├── app.py
├── config.py
├── models.py
├── forms.py
├── utils.py
├── payment_providers.py
├── escrow.py
├── dispute_resolution.py
├── tasks.py
├── telegram_bot.py
├── api/
│   ├── __init__.py
│   ├── users.py
│   ├── transactions.py
│   ├── auctions.py
│   ├── bids.py
│   ├── orders.py
│   ├── messages.py
│   └── disputes.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── kyc.html
│   ├── deposit.html
│   ├── withdraw.html
│   ├── balance.html
│   ├── new_auction.html
│   ├── auction_detail.html
│   ├── my_auctions.html
│   ├── my_bids.html
│   ├── order_detail.html
│   ├── open_dispute.html
│   ├── messages.html
│   ├── profile.html
│   └── support.html
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── migrations/
├── .env
└── requirements.txt



9. Развертывание и Запуск Приложения

Установка Зависимостей:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Настройка Переменных Окружения (.env):

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost/auction_db
COINBASE_COMMERCE_API_KEY=your_coinbase_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

Инициализация Базы Данных:

flask db init
flask db migrate
flask db upgrade

Запуск Приложения:

flask run

Запуск Планировщика Задач:

python tasks.py

Запуск Telegram-Бота:

python telegram_bot.py



10. Диаграммы



10.1. Диаграмма Вариантов Использования (Use Case Diagram)

@startuml
left to right direction
skinparam packageStyle rectangle

actor Пользователь
actor Администратор

rectangle "Бот-Аукцион" {
    usecase "Регистрация/Аутентификация" as UC1
    usecase "Верификация KYC" as UC2
    usecase "Управление балансом USDC" as UC3
    usecase "Создание аукциона" as UC4
    usecase "Участие в аукционе" as UC5
    usecase "Передача товара/услуги" as UC6
    usecase "Разрешение споров" as UC7
    usecase "Оставление отзывов" as UC8
    usecase "Модерация споров" as UC9
}

Пользователь --> UC1
Пользователь --> UC2
Пользователь --> UC3
Пользователь --> UC4
Пользователь --> UC5
Пользователь --> UC6
Пользователь --> UC7
Пользователь --> UC8

Администратор --> UC9

@enduml



10.2. Диаграмма Классов (Class Diagram)

@startuml
class User {
    +id: Integer
    +telegram_id: String
    +email: String
    +password_hash: String
    +username: String
    +kyc_status: String
    +is_active: Boolean
    +created_at: DateTime
    +updated_at: DateTime
    ---
    +register()
    +login()
    +verify_kyc()
}

class Wallet {
    +id: Integer
    +user_id: Integer
    +balance_usdc: Decimal
    +deposit_address: String
    ---
    +deposit()
    +withdraw()
}

class Transaction {
    +id: Integer
    +wallet_id: Integer
    +type: String
    +amount_usdc: Decimal
    +status: String
    +transaction_hash: String
    ---
    +process()
}

class Auction {
    +id: Integer
    +seller_id: Integer
    +title: String
    +description: String
    +starting_price: Decimal
    +current_price: Decimal
    +end_time: DateTime
    +is_active: Boolean
    ---
    +create()
    +place_bid()
    +close()
}

class Bid {
    +id: Integer
    +auction_id: Integer
    +bidder_id: Integer
    +amount: Decimal
    +created_at: DateTime
}

class Order {
    +id: Integer
    +auction_id: Integer
    +buyer_id: Integer
    +seller_id: Integer
    +status: String
    +shipping_address: String
    +tracking_number: String
    ---
    +update_status()
}

class Message {
    +id: Integer
    +sender_id: Integer
    +recipient_id: Integer
    +content: String
    +created_at: DateTime
}

class Dispute {
    +id: Integer
    +order_id: Integer
    +initiator_id: Integer
    +reason: String
    +status: String
    ---
    +open()
    +resolve()
}

class Review {
    +id: Integer
    +order_id: Integer
    +reviewer_id: Integer
    +rating: Integer
    +comment: String
    +created_at: DateTime
}

User "1" -- "1" Wallet
User "1" -- "0..*" Auction : "создает"
User "1" -- "0..*" Bid : "делает"
User "1" -- "0..*" Order : "покупает"
User "1" -- "0..*" Message : "отправляет"
User "1" -- "0..*" Dispute : "инициирует"
User "1" -- "0..*" Review : "оставляет"

Auction "1" -- "0..*" Bid : "имеет"
Auction "1" -- "1" Order : "создает"
Order "1" -- "1" Dispute : "может иметь"
Order "1" -- "1" Review : "может иметь"

@enduml



10.3. Диаграмма Объектов (Object Diagram)

@startuml
object user1 {
    id = 1
    username = "alice"
    kyc_status = "verified"
}

object wallet1 {
    id = 1
    user_id = 1
    balance_usdc = 100.0
}

object auction1 {
    id = 1
    seller_id = 1
    title = "Laptop for sale"
    current_price = 500.0
    is_active = true
}

object bid1 {
    id = 1
    auction_id = 1
    bidder_id = 2
    amount = 550.0
}

user1 -- wallet1
user1 -- auction1 : "продает"
auction1 -- bid1 : "имеет ставку"

@enduml



10.4. Диаграммы Последовательности (Sequence Diagrams)

Пример: Регистрация и Верификация Пользователя

@startuml
actor Пользователь
participant "Веб-приложение" as WebApp
participant "База данных" as Database
participant "Сервис KYC/AML" as KYCService

Пользователь -> WebApp : Заполнение формы регистрации
WebApp -> Database : Сохранение данных пользователя
WebApp -> Пользователь : Подтверждение регистрации

Пользователь -> WebApp : Загрузка документов для KYC
WebApp -> KYCService : Отправка документов
KYCService -> WebApp : Результат проверки
WebApp -> Database : Обновление статуса KYC
WebApp -> Пользователь : Уведомление о статусе верификации

@enduml

Пример: Создание Аукциона и Делание Ставки

@startuml
actor Продавец
participant "Веб-приложение" as WebApp
participant "База данных" as Database

Продавец -> WebApp : Создание аукциона
WebApp -> Database : Сохранение аукциона
WebApp -> Продавец : Подтверждение создания

actor Покупатель

Покупатель -> WebApp : Просмотр аукциона
Покупатель -> WebApp : Делает ставку
WebApp -> Database : Проверка баланса
WebApp -> Database : Сохранение ставки
WebApp -> Покупатель : Подтверждение ставки
WebApp -> Продавец : Уведомление о новой ставке

@enduml



10.5. Диаграммы Деятельности (Activity Diagrams)

Пример: Процесс Делания Ставки

@startuml
start
:Покупатель выбирает аукцион;
if (Аукцион активен?) then (да)
  :Покупатель вводит сумму ставки;
  :Проверка баланса;
  if (Достаточно средств?) then (да)
    :Ставка принимается;
    :Обновление текущей цены;
    :Уведомление продавца;
  else (нет)
    :Сообщение об ошибке;
  endif
else (нет)
  :Сообщение, что аукцион закрыт;
endif
stop
@enduml



10.6. Диаграмма Компонентов (Component Diagram)

@startuml
component "Веб-приложение\n(Flask)" as WebApp
component "Telegram-бот" as TelegramBot
database "База данных\n(PostgreSQL)" as Database
component "Платежный провайдер\n(Coinbase Commerce)" as PaymentProvider
component "Сервисы KYC/AML" as KYCService
component "Планировщик задач\n(APScheduler)" as Scheduler

WebApp --> Database
WebApp --> PaymentProvider
WebApp --> TelegramBot
WebApp --> KYCService
Scheduler --> WebApp

@enduml



10.7. Диаграмма Развертывания (Deployment Diagram)

@startuml
node "Пользовательское устройство" {
    [Браузер]
    [Telegram-клиент]
}

node "Сервер приложений" {
    component "Веб-приложение (Flask)" as WebApp
    component "Telegram-бот" as TelegramBot
    component "Планировщик задач (APScheduler)" as Scheduler
}

node "Сервер базы данных" {
    database "PostgreSQL" as Database
}

node "Платежный провайдер" {
    component "Coinbase Commerce API" as PaymentProvider
}

node "Сервис KYC" {
    component "KYC/AML Service" as KYCService
}

[Bраузер] --> WebApp
[Telegram-клиент] --> TelegramBot
WebApp --> Database
WebApp --> PaymentProvider
WebApp --> KYCService
Scheduler --> WebApp

@enduml



10.8. Диаграммы Состояний (State Diagrams)

Пример: Состояния Аукциона

@startuml
[*] --> Создан
Создан --> Активен : Время начала
Активен --> Завершен : Время окончания
Активен --> Завершен : Продавец завершил
Завершен --> [*]

@enduml

Пример: Состояния Заказа

@startuml
[*] --> Pending
Pending --> Shipped : Продавец отправил товар
Shipped --> Delivered : Покупатель подтвердил получение
Shipped --> Delivered : Автоматическое подтверждение
Delivered --> Completed : Средства освобождены
Pending --> Disputed : Открыт спор
Shipped --> Disputed : Открыт спор
Delivered --> Disputed : Открыт спор
Disputed --> Resolved : Спор решен
Resolved --> Completed

@enduml



10.9. Диаграмма Времени (Timing Diagram)

Пример: Процесс Завершения Аукциона и Освобождения Средств

@startuml
robust "Покупатель" as Buyer
robust "Эскроу-счет" as Escrow
robust "Продавец" as Seller

@0 Buyer is "Имеет средства"
@1 Buyer is "Средства заморожены"
@2 Seller is "Отправляет товар"
@3 Buyer is "Получает товар"
@4 Buyer is "Подтверждает получение"
@5 Escrow is "Освобождает средства"
@6 Seller is "Получает средства"

@enduml



11. Заключение

Данный документ предоставляет полное и детальное описание архитектуры приложения “Бот-Аукцион” с интеграцией USDC. Он включает в себя описание компонентов системы, модели данных, функциональные компоненты с примерами реализации, меры безопасности, используемые технологии и инструменты, структуру проекта, а также различные UML-диаграммы для визуализации архитектуры.

Рекомендуемые Шаги:

    1.	Настройка Окружения: Установить все необходимые инструменты и зависимости.
    2.	Создание Базы Данных: Определить модели и выполнить миграции.
    3.	Реализация Основных Функций: Регистрация, аутентификация, KYC.
    4.	Интеграция с Платежным Провайдером: Настроить взаимодействие с Coinbase Commerce.
    5.	Разработка Функционала Аукционов: Создание, участие, завершение.
    6.	Внедрение Эскроу-Системы: Реализовать заморозку и освобождение средств.
    7.	Разработка Системы Споров: Открытие, модерация, разрешение.
    8.	Обеспечение Безопасности: Внедрить все описанные меры безопасности.
    9.	Тестирование: Написать и выполнить тесты для всех компонентов.
    10.	Документация: Подготовить документацию для пользователей и разработчиков.

Важно: Постоянно консультируйтесь с юридическими специалистами по вопросам соответствия законодательству в области криптовалют и электронной коммерции.

Полезные Ресурсы:

    •	Flask Documentation: https://flask.palletsprojects.com/
    •	SQLAlchemy Documentation: https://docs.sqlalchemy.org/
    •	Coinbase Commerce API: https://commerce.coinbase.com/docs/api/
    •	python-telegram-bot Documentation: https://python-telegram-bot.org/
    •	Web3.py Documentation: https://web3py.readthedocs.io/
    •	PlantUML: https://plantuml.com/ru/

Примечание: Для визуализации UML-диаграмм скопируйте код PlantUML в соответствующий редактор, например, PlantUML Online Server.

