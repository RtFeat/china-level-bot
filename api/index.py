from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def webapp():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_delivery():
    try:
        data = request.json
        
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
        
        # Базовая стоимость доставки
        base_rates = {
            'Обычные товары': {
                'low_density': 4,
                'medium_density': 6,
                'high_density': 8
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
        
        # Базовая стоимость доставки
        delivery_cost = volume * rate
        
        # Стоимость упаковки
        packaging_costs = {
            'Мешок': 5,
            'Картонные уголки': volume * 20,
            'Деревянная обрешетка': volume * 27,
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
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при расчете стоимости'}), 500

# Экспорт для Vercel
application = app

if __name__ == "__main__":
    app.run()