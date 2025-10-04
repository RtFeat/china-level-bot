from telebot import types
import time
import traceback
import os
import telebot
from dotenv import load_dotenv
import logging
from flask import Flask, render_template, request, jsonify
import threading

# Отладка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    TOKEN = input("Введите токен вашего бота: ")
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Инициализация Flask приложения
app = Flask(__name__)

# Определяем словарь responses в глобальной области видимости
responses = {
    "Стоимость доставки из Китая": (
        "💰<b>Стоимость доставки из Китая</b>\n\n"
        " Стоимость доставки напрямую зависит от <i>плотности и категории товара!</i>\n\n"
        "Для расчета потребуются следующие данные о вашем товаре:\n\n"
        "• <b>Категория</b> (хоз. товар, одежда, обувь)\n"
        "• <b>Вес</b>, кг\n"
        "• <b>Объем</b>, куб. м.\n"
        "• <b>Габариты</b> (длина, ширина, высота) – если известен объем, эти данные можно не заполнять.\n\n"
        "📄 Ниже прикрепляем наш прайс. Зная плотность товара (<i>плотность = кг/куб. м.</i>) вы можете самостоятельно определить стоимость по таблице.\n\n"
        "Обратите внимание: все товары, за исключением одежды и обуви, относятся к хозяйственным товарам."
    ),
    "Упаковка товаров перед отправкой": (
        "📦<b>Упаковка товаров перед отправкой</b>\n\n"
        " Перед отправкой в Россию товар необходимо надежно упаковать. Мы предлагаем следующие варианты упаковки:\n\n"
        "• Водонепроницаемый пакет + двойной мешок + двойной скотч (подходит для перевозки мягких, не хрупких товаров) – *5$*\n"
        "• Усиление картонными уголками (если важно сохранить целостность упаковки) – <i>6$/место, 0,3 м³</i>\n"
        "• Усиление деревянной обрешеткой (для хрупкого, дорогого, габаритного груза) – <i>8$/место, 0,3 м³</i>\n"
        "• Паллет (наиболее надежный вид упаковки, груз закреплен деревянной обрешеткой) – <i>35$/1 м³</i>\n"
        "• Деревянный ящик (самая крепкая упаковка для перевозки дорогих, хрупких товаров) – <i>100$/1 м³</i>"
    ),
    "Бонусы и привилегии": (
        "🎁 <b>Бонусы и привилегии</b>\n\n"
        "Ознакомьтесь с нашими бонусами и привилегиями для клиентов в зависимости от ежемесячного оборота заказа.\n\n"
        "📄 Ниже прикрепляем PDF-документ с подробной информацией."
    ),
    "Поиск товаров": (
        "🔍 <b>Поиск товаров</b>\n\n"
        "Мы подходим к поиску комплексно, поэтому вы получаете контакты проверенных поставщиков. Вот что мы делаем:\n\n"
        "• Проводим анализ деловой репутации поставщика.\n"
        "• Проверяем наличие необходимых сертификатов.\n"
        "• Оцениваем отзывы клиентов на китайских площадках.\n"
        "• Ищем товары в соответствии с вашими требованиями и бюджетом.\n\n"
        "💵 Стоимость от <i>3000 руб.</i> в зависимости от сложности товара.\n"
        "<b>Стоимость услуги будет вычтена из суммы комиссии</b>\n\n"
    ),
    "Поиск фабрик": (
        "🏭 <b>Поиск фабрик</b>\n\n"
        "Мы применяем комплексный подход:\n\n"
        "• Анализируем деловую репутацию поставщика.\n"
        "• Проверяем наличие необходимых сертификатов.\n"
        "• Изучаем отзывы клиентов на китайских площадках.\n"
        "• Ищем фабрики по вашим требованиям и бюджету.\n\n"
        "📁 В результате вы получаете подробные каталоги каждого производителя.\n"
        "💵 Стоимость от <i>5000 руб.</i> в зависимости от сложности товара.\n"
        "<b>Стоимость услуги будет вычтена из суммы комиссии</b>\n\n"
    ),
    "Переговоры с поставщиком": (
        "🤝 <b>Переговоры с поставщиком</b>\n\n"
        "Если необходимо уточнить детали сделки, задать дополнительные вопросы или узнать о наличии товара и сроках доставки внутри Китая, воспользуйтесь нашей услугой переговоров.\n\n"
        "Мы уточним:\n"
        "• Условия работы по брендированию или производству уникального товара (OEM/ODM).\n"
        "• Детальную информацию о технических характеристиках товара.\n"
        "• Условия получения скидок при оптовых закупках.\n"
        "• Расчет стоимости и сроков доставки внутри Китая.\n"
        "• Фото- и видеоматериалы товара и его упаковки.\n"
        "• Размеры и вес упаковочных коробов.\n"
        "• Актуальные данные о наличии продукции на складе.\n"
        "• Стоимость 1500 рублей, \n"
        "! Не более двух поставщиков\n"
        "<b>Стоимость услуги будет вычтена из суммы комиссии</b>\n\n"
    ),
    "Доставка образцов в РФ": (
        "✈️ <b>Доставка образцов в РФ</b>\n\n"
        "Чтобы избежать неприятных сюрпризов, рекомендуем заказывать образцы товаров заранее. Обратите внимание: доставка образцов осуществляется исключительно авиаперевозкой.\n\n"
        "💵 Стоимость услуги: <i>1500 руб.</i>\n"
        "📦 В услугу входит доставка до 7 товаров от 7 поставщиков.\n"
        "📞 Услуга общения с поставщиком, а также фото/видео обзор оплачиваются отдельно.\n"
        "🔗 Перед началом работы мы запрашиваем ссылку на товар."
    ),
    "Условия выкупа товаров": (
        "💼 <b>Условия выкупа товаров</b>\n\n"
        "Комиссия рассчитывается исходя из стоимости вашего товара:\n\n"
        "• 50 000 руб – 199 000 руб – <i>7%</i>\n"
        "• 200 000 руб – 499 000 руб – <i>5%</i>\n"
        "• 500 000 руб – 799 000 руб – <i>4%</i>\n"
        "• 800 000 руб – 999 999 руб – <i>3%</i>\n"
        "• Выше 1 000 000 руб – 1 499 000 <i>1,5%</i>\n"
        "• Свыше 1 500 000 <i>1%</i>\n\n"
        "В стоимость комиссии входит общение с поставщиками (не более 2, каждый дополнительный поставщик оплачивается отдельно по прайсу)."
    ),
    "OEM/ODM - производство": (
        "🏷️ <b>OEM/ODM - производство</b>\n\n"
        "• <b>OEM</b> – производство товаров по вашим брендовым требованиям с использованием стандартных шаблонов фабрики.\n"
        "  Пример: если фабрика выпускает базовые футболки черного и белого цвета, вы можете заказать их в зеленом или голубом цвете с вашим логотипом.\n"
        "  💵 Стоимость: от <i>7 тысяч руб.</i> за товар.\n\n"
        "• <b>ODM</b> – производство товаров по уникальному техническому заданию заказчика, с разработкой дизайна и выпуском продукции под вашим брендом.\n"
        "  💵 Стоимость: от <i>10 тыс. руб.</i> за товар."
    ),
    "Базовая проверка поставщика": (
        "📔 <b>В услугу входит отчет с информацией о:</b>\n\n"
        "Рейтинге на платформах;\n"
        "Наличии/отсутствии сертификатов, разрешительных документов;\n"
        "Основном виде деятельности, сфере деятельности (поставщик/фабрика);\n"
        "Организационно-правовой форме и учредителе;\n"
        "Наличии/отсутствии судебных дел и штрафов;\n"
        "Контактной информации и адресах;\n"
        "Официально-устроенном персонале;\n"
        "Оборотах компании.\n\n"
        "💵<b> Стоимость 5 000 рублей проверка 1-2 поставщиков.</b>"
    ),
    "Полное сопровождение сделки": (
        "<b>В данную услугу входит:</b>\n\n"
        "Поиск товара/поставщика, переговоры, выкуп, организация доставки.\n"
        "За вами закрепляется менеджер, который будет сопровождать вас на этапе ведения сделки.\n\n"
        "💵 <b>Стоимость 20 000 рублей в месяц.</b>"
    )
}

# Flask маршруты для веб-приложения калькулятора
@app.route('/')
def webapp():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_delivery():
    try:
        data = request.json
        logger.info(f"Получены данные для расчета: {data}")
        
        # Извлекаем данные из запроса
        category = data.get('category', 'Обычные товары')
        product_cost = float(data.get('product_cost', 0))
        volume = float(data.get('volume', 0))
        weight = float(data.get('weight', 0))
        packaging = data.get('packaging', 'Мешок')
        delivery_speed = data.get('delivery_speed', 'Стандартная (15-20 дней)')
        insurance = data.get('insurance', False)
        unloading = data.get('unloading', False)
        
        # Валидация данных
        if volume <= 0 or weight <= 0:
            return jsonify({'error': 'Объем и вес должны быть больше 0'}), 400
        
        # Расчет плотности
        density = weight / volume if volume > 0 else 0
        
        # Базовая стоимость доставки (примерные тарифы)
        base_rates = {
            'Обычные товары': {
                'low_density': 4,  # до 200 кг/м³
                'medium_density': 6,  # 200-400 кг/м³ 
                'high_density': 8   # свыше 400 кг/м³
            },
            'Одежда': {
                'low_density': 3,
                'medium_density': 4,
                'high_density': 5
            },
            'Обувь': {
                'low_density': 5,
                'medium_density': 7,
                'high_density': 9
            }
        }
        
        # Определяем тариф по плотности
        if density <= 200:
            rate = base_rates[category]['low_density']
        elif density <= 400:
            rate = base_rates[category]['medium_density']
        else:
            rate = base_rates[category]['high_density']
        
        # Базовая стоимость доставки (используем объем для расчета)
        delivery_cost = volume * rate
        
        # Стоимость упаковки
        packaging_costs = {
            'Мешок': 5,
            'Картонные уголки': volume * 20,  # 6$/0.3м³ = ~20$/м³
            'Деревянная обрешетка': volume * 27,  # 8$/0.3м³ = ~27$/м³
            'Паллет': volume * 35,
            'Деревянный ящик': volume * 100
        }
        
        packaging_cost = packaging_costs.get(packaging, 0)
        
        # Коэффициент скорости доставки
        speed_multiplier = {
            'Стандартная (15-20 дней)': 1.0,
            'Ускоренная (10-12 дней)': 1.3,
            'Экспресс (5-7 дней)': 1.8
        }
        
        delivery_cost *= speed_multiplier.get(delivery_speed, 1.0)
        
        # Страховка (1% от стоимости товара)
        insurance_cost = product_cost * 0.01 if insurance else 0
        
        # Разгрузка (примерно 50 руб/м³)
        unloading_cost = volume * 50 if unloading else 0
        
        # Комиссия
        if product_cost < 50000:
            commission_rate = 0.07
        elif product_cost < 200000:
            commission_rate = 0.07
        elif product_cost < 500000:
            commission_rate = 0.05
        elif product_cost < 800000:
            commission_rate = 0.04
        elif product_cost < 1000000:
            commission_rate = 0.03
        elif product_cost < 1500000:
            commission_rate = 0.015
        else:
            commission_rate = 0.01
        
        commission = product_cost * commission_rate
        
        # Общая стоимость
        total_cost = delivery_cost + packaging_cost + insurance_cost + unloading_cost + commission
        
        result = {
            'delivery_cost': round(delivery_cost, 2),
            'packaging_cost': round(packaging_cost, 2),
            'insurance_cost': round(insurance_cost, 2),
            'unloading_cost': round(unloading_cost, 2),
            'commission': round(commission, 2),
            'total_cost': round(total_cost, 2),
            'density': round(density, 2),
            'commission_rate': f"{commission_rate*100}%"
        }
        
        logger.info(f"Результат расчета: {result}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Ошибка при расчете: {str(e)}")
        return jsonify({'error': 'Ошибка при расчете стоимости'}), 500

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

def send_main_menu(chat_id):
    webapp_url = 'https://china-level-bot.vercel.app/' 

    bot.send_message(chat_id, "Команда China level приветствует Вас!\n"
                     "Берем на себя все вопросы по работе с Китаем от поиска до доставки в РФ, найдем, проверим, выкупим и доставим Ваш товар в Россию.\n\n"
                     "Почему мы?🚀\n\n"
                     "🏗Наши склады расположены в 4 городах Китая и в Москве, общей площадью более 7,5 тыс. квадратных метров\n"
                     "⭐️Бесплатное хранение товара на складе в Москве до 1 месяца\n"
                     "🤝За 7 лет работы собрали базу лучших поставщиков самых разных категорий товаров\n\n"
                     "Если у Вас есть вопрос или нужна помощь - ждем вашего звонка или сообщения:\n"
                     "telegram: @ChinaLevelManager\n"
                     "Whatsapp: +7(918)596-31-87\n"
                     "Insta: @china.level -  https://clck.ru/3GKPJE \n"
                     "Наш сайт: chinalevel.com\n")

    webapp_keyboard = types.InlineKeyboardMarkup()
    webapp_btn = types.InlineKeyboardButton('📦 Точный расчет', web_app=types.WebAppInfo(url=webapp_url))
    webapp_keyboard.add(webapp_btn)
    
    try:
        bot.send_message(chat_id, "Рассчитайте стоимость доставки:", reply_markup=webapp_keyboard)
    except Exception as e:
        logger.error(f"Error sending webapp message: {str(e)}")
        bot.send_message(chat_id, "Ошибка при загрузке калькулятора. Пожалуйста, используйте ручной расчет или свяжитесь с менеджером.")

    keyboard1 = types.InlineKeyboardMarkup()
    key_delivery = types.InlineKeyboardButton(text='\U0001F4B0 Стоимость доставки из Китая', callback_data='Стоимость доставки из Китая')
    key_packaging = types.InlineKeyboardButton(text='\U0001F6CD Упаковка товаров перед отправкой', callback_data='Упаковка товаров перед отправкой')
    key_calculator = types.InlineKeyboardButton(text='🧮 Калькулятор доставки', web_app=types.WebAppInfo(url=webapp_url))  # Замените на ваш HTTPS URL!
    key_bonuses = types.InlineKeyboardButton(text='🎁 Бонусы и привилегии', callback_data='Бонусы и привилегии')
    keyboard1.row(key_delivery)
    keyboard1.row(key_packaging)
    keyboard1.row(key_calculator)
    keyboard1.row(key_bonuses)
    
    try:
        bot.send_message(chat_id, "Основные услуги:", reply_markup=keyboard1)
    except Exception as e:
        logger.error(f"Error sending keyboard1: {str(e)}")
        bot.send_message(chat_id, "Ошибка при отображении основных услуг.")

    keyboard2 = types.InlineKeyboardMarkup()
    key_products = types.InlineKeyboardButton(text='\U0001F50D Поиск товаров', callback_data='Поиск товаров')
    key_supliers = types.InlineKeyboardButton(text='\U0001F3ED Поиск фабрик', callback_data='Поиск фабрик')
    key_talks = types.InlineKeyboardButton(text='\U0001F4AC Переговоры с поставщиком', callback_data='Переговоры с поставщиком')
    key_sample = types.InlineKeyboardButton(text='\U0001F69A Доставка образцов в РФ', callback_data='Доставка образцов в РФ')
    key_ransom = types.InlineKeyboardButton(text='Условия выкупа товаров', callback_data='Условия выкупа товаров')
    key_manufacturing = types.InlineKeyboardButton(text='\U0001F45A OEM/ODM - производство', callback_data='OEM/ODM - производство')
    key_check = types.InlineKeyboardButton(text='🔮 Базовая проверка поставщика', callback_data='Базовая проверка поставщика')
    key_withyou = types.InlineKeyboardButton(text='🤝 Полное сопровождение сделки', callback_data='Полное сопровождение сделки')
    keyboard2.row(key_products)
    keyboard2.row(key_supliers)
    keyboard2.row(key_talks)
    keyboard2.row(key_sample)
    keyboard2.row(key_ransom)
    keyboard2.row(key_manufacturing)
    keyboard2.row(key_check)
    keyboard2.row(key_withyou)
    bot.send_message(chat_id, "Дополнительные услуги:", reply_markup=keyboard2)

    markup = types.InlineKeyboardMarkup()
    btn_whatsapp = types.InlineKeyboardButton(text='Whats App', url='https://wa.me/qr/55SW5T77PVKLE1')
    btn_telegram = types.InlineKeyboardButton(text='Telegram', url='https://t.me/ChinaLevelManager')
    markup.add(btn_whatsapp)
    markup.add(btn_telegram)
    bot.send_message(chat_id, "Для связи с нашим менеджером", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_animation(message.chat.id, animation='https://media.giphy.com/media/wEhdsAyB3Ijza4AL7L/giphy.gif?cid=790b7611h2lw2astv331nd88a0zzol66vu7m835azfytsmvl&ep=v1_gifs_search&rid=giphy.gif&ct=g')
    time.sleep(1)
    send_main_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    logger.info(f"Получен callback: {call.data}")

    # Обработка кнопки "Назад"
    if call.data == "back_to_main":
        logger.info(f"Обработка кнопки 'Назад', удаление сообщения ID: {call.message.message_id}")
        try:
            # Удаляем текущее сообщение (с деталями услуги)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {str(e)}")
        
        # Отправляем главное меню заново
        send_main_menu(call.message.chat.id)
        return

    # Обработка остальных кнопок
    if call.data in responses:
        # 🌀 Эффект "бот думает"
        bot.send_chat_action(call.message.chat.id, 'typing')
        time.sleep(1.2)

        # Создаём клавиатуру с кнопкой "Назад"
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)

        # Редактируем сообщение
        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                 message_id=call.message.message_id,
                                 text=responses[call.data],
                                 reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Ошибка при редактировании сообщения: {str(e)}")
            bot.send_message(call.message.chat.id, "Произошла ошибка при обработке запроса. Попробуйте снова.")

        # Отправка документа и ссылки, если выбрана "Стоимость доставки из Китая"
        if call.data == "Стоимость доставки из Китая":
            try:
                # Используем относительный путь (предполагая, что файл в той же директории или поддиректории)
                delivery_price_path = os.path.join(os.path.dirname(__file__), 'delivery_price.xlsx')
                with open(delivery_price_path, 'rb') as file:
                    bot.send_document(chat_id=call.message.chat.id, document=file, caption="Прайс-лист на доставку")
            except FileNotFoundError:
                bot.send_message(call.message.chat.id, "Извините, файл с прайсом не найден.")
            except Exception as e:
                logger.error(f"Ошибка при отправке файла: {str(e)}")

        # Отправка PDF с бонусами и привилегиями
        if call.data == "Бонусы и привилегии":
            try:
                # Используем относительный путь
                bonuses_path = os.path.join(os.path.dirname(__file__), 'privileges.pdf')
                with open(bonuses_path, 'rb') as file:
                    bot.send_document(chat_id=call.message.chat.id, document=file, caption="Бонусы и привилегии для клиентов")
            except FileNotFoundError:
                bot.send_message(call.message.chat.id, "Извините, файл с бонусами и привилегиями не найден.")
            except Exception as e:
                logger.error(f"Ошибка при отправке файла: {str(e)}")
    else:
        logger.warning(f"Неизвестный callback: {call.data}")
        bot.send_message(call.message.chat.id, "Неизвестная команда")

if __name__ == '__main__':
    # Запуск Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запуск бота
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            logger.error(f"Ошибка в боте: {str(e)}")
            traceback.print_exc()
            bot.stop_polling()
            time.sleep(15)