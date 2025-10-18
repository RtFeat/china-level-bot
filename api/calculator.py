from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Таблицы ставок из Excel (Sheet1)
# Стандартная доставка (строки 2-4)
STANDARD_RATES = {
    'Одежда': {
        100: 480, 110: 4.7, 120: 4.6, 130: 4.5, 140: 4.4, 150: 4.3, 160: 4.2, 170: 4.1,
        180: 4, 190: 3.9, 200: 3.8, 250: 3.7, 300: 3.7, 350: 3.65, 400: 3.65, 450: 3.6,
        500: 3.6, 600: 3.6, 700: 3.6, 800: 3.6, 900: 3.6, 1000: 3.6, 100000: 3.55
    },
    'Обувь': {
        100: 400, 110: 4.1, 120: 4, 130: 3.9, 140: 3.8, 150: 3.7, 160: 3.6, 170: 3.5,
        180: 3.4, 190: 3.3, 200: 3.2, 250: 3.1, 300: 3.1, 350: 3.1, 400: 3.1, 450: 3.1,
        500: 3.1, 600: 3.1, 700: 3.1, 800: 3.1, 900: 3.1, 1000: 3.1, 100000: 3.1
    },
    'Хозтовары': {
        100: 330, 110: 3.1, 120: 3, 130: 2.9, 140: 2.8, 150: 2.7, 160: 2.6, 170: 2.5,
        180: 2.4, 190: 2.3, 200: 2.2, 250: 2.1, 300: 2, 350: 1.9, 400: 1.8, 450: 1.7,
        500: 1.65, 600: 1.65, 700: 1.6, 800: 1.6, 900: 1.6, 1000: 1.6, 100000: 1.5
    }
}

# Ускоренная доставка (строки 9-11)
EXPRESS_RATES = {
    'Одежда': {
        100: 470, 110: 4.5, 120: 4.4, 130: 4.3, 140: 4.2, 150: 4.1, 160: 4, 170: 3.9,
        180: 3.8, 190: 3.7, 200: 3.6, 250: 3.5, 300: 3.5, 350: 3.45, 400: 3.45, 450: 3.4,
        500: 3.4, 600: 3.4, 700: 3.4, 800: 3.4, 900: 3.4, 1000: 3.4, 100000: 3.35
    },
    'Обувь': {
        100: 390, 110: 3.9, 120: 3.8, 130: 3.7, 140: 3.6, 150: 3.5, 160: 3.4, 170: 3.3,
        180: 3.2, 190: 3.1, 200: 3, 250: 2.9, 300: 2.9, 350: 2.9, 400: 2.9, 450: 2.9,
        500: 2.9, 600: 2.9, 700: 2.9, 800: 2.9, 900: 2.9, 1000: 2.9, 100000: 2.9
    },
    'Хозтовары': {
        100: 320, 110: 2.9, 120: 2.8, 130: 2.7, 140: 2.6, 150: 2.5, 160: 2.4, 170: 2.3,
        180: 2.2, 190: 2.1, 200: 2, 250: 1.9, 300: 1.8, 350: 1.7, 400: 1.6, 450: 1.5,
        500: 1.45, 600: 1.45, 700: 1.4, 800: 1.4, 900: 1.4, 1000: 1.4, 100000: 1.3
    }
}

def get_rate_by_density(rates_table, category, density):
    """Находит ставку по плотности из таблицы"""
    if category not in rates_table:
        category = 'Хозтовары'
    
    category_rates = rates_table[category]
    density_keys = sorted(category_rates.keys())
    
    # Находим подходящую ставку
    for key in density_keys:
        if density <= key:
            return category_rates[key]
    
    # Если плотность больше максимальной, берем последнюю ставку
    return category_rates[density_keys[-1]]

@app.route('/')
def webapp():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_delivery():
    try:
        data = request.json
        
        # Извлекаем данные из запроса
        category = data.get('category', 'Хозтовары')
        if category == 'Обычные товары':
            category = 'Хозтовары'
        
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
        
        # Расчет плотности по формуле E31 = F4/F6 (вес/объем)
        density = weight / volume  # кг/м³
        
        # ЛОГИСТИКА
        # Выбираем таблицу ставок в зависимости от скорости доставки
        if delivery_speed == 'Ускоренная (10-12 дней)':
            rates_table = EXPRESS_RATES
        else:
            rates_table = STANDARD_RATES
        
        # Получаем ставку из таблицы по плотности
        rate = get_rate_by_density(rates_table, category, density)
        
        # Формула H6/H8: =ЕСЛИ(E31>100, E30*F4, ЕСЛИ(E31<100, E30*F6))
        # E31 - это плотность (вес/объем) в кг/м³
        # E30 - это rate из таблицы
        # F4 - это weight (вес) в кг
        # F6 - это volume (объем) в м³
        
        if density > 100:
            # Плотность > 100 кг/м³ - умножаем ставку на вес
            delivery_cost = rate * weight
        else:
            # Плотность < 100 кг/м³ - умножаем ставку на объем
            delivery_cost = rate * volume
        
        # Для экспресс доставки применяем дополнительный множитель
        if delivery_speed == 'Экспресс (5-7 дней)':
            delivery_cost *= 1.8
        
        # СТРАХОВКА
        # Формула: =ЕСЛИ((F12/F4)<30, F12*0.01, ЕСЛИ(F12/F4<50, F12*0.02, F12*0.03))
        if insurance:
            ratio = product_cost / volume
            if ratio < 30:
                insurance_cost = product_cost * 0.01
            elif ratio < 50:
                insurance_cost = product_cost * 0.02
            else:
                insurance_cost = product_cost * 0.03
        else:
            insurance_cost = 0
        
        # РАЗГРУЗКА
        # Формула: =ЕСЛИ(F6<10, 5.8*F6, ЕСЛИ(F6>10, 4.5*F6))
        if unloading:
            if volume < 10:
                unloading_cost = 5.8 * volume
            else:
                unloading_cost = 4.5 * volume
        else:
            unloading_cost = 0
        
        # УПАКОВКА
        # Формула: =ЕСЛИ(H2=1, F6/0.3*3, ЕСЛИ(H2=2, F6/0.3*5, ...))
        packaging_costs = {
            'Мешок': (volume / 0.3) * 3,
            'Картонные уголки': (volume / 0.3) * 5,
            'Деревянная обрешетка': (volume / 0.3) * 7,
            'Паллет': (volume / 1) * 35,
            'Деревянный ящик': (volume / 1) * 85
        }
        
        packaging_cost = packaging_costs.get(packaging, 0)
        
        # КОМИССИЯ (не включается в итог по Excel)
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
        
        # ИТОГО (формула из Excel: =F22+F24+F20+H16)
        total_cost = delivery_cost + packaging_cost + insurance_cost + unloading_cost
        
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
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Ошибка при расчете стоимости: {str(e)}'}), 500

# Экспорт для Vercel
application = app

if __name__ == "__main__":
    app.run()