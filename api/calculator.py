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
        
        # ЛОГИСТИКА - Базовая стоимость доставки в зависимости от категории и плотности
        # Формула из Excel: =ЕСЛИ(H3=1,H6*1,ЕСЛИ(H3=2,H8*1))
        # H3 - это скорость доставки, H6/H8 - базовые тарифы
        
        # Определяем базовый тариф по категории и плотности
        if category == 'Обычные товары':
            if density <= 200:
                base_rate = 4
            elif density <= 400:
                base_rate = 6
            else:
                base_rate = 8
        elif category == 'Одежда':
            if density <= 200:
                base_rate = 3
            elif density <= 400:
                base_rate = 4
            else:
                base_rate = 5
        else:  # Обувь
            if density <= 200:
                base_rate = 5
            elif density <= 400:
                base_rate = 7
            else:
                base_rate = 9
        
        # Базовая стоимость логистики (по объему)
        base_logistics = volume * base_rate
        
        # Применяем множитель скорости доставки
        if delivery_speed == 'Стандартная (15-20 дней)':
            delivery_cost = base_logistics * 1.0
        elif delivery_speed == 'Ускоренная (10-12 дней)':
            delivery_cost = base_logistics * 1.3
        else:  # Экспресс
            delivery_cost = base_logistics * 1.8
        
        # СТРАХОВКА
        # Формула из Excel: =ЕСЛИ((F12/F4)<30,F12*0.01,ЕСЛИ(F12/F4<50,F12*0.02,ЕСЛИ(F12/F4<100000000000000000000,F12*0.03)))
        # F12 - стоимость товара, F4 - объем
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
        # Формула из Excel: =ЕСЛИ(F6<10,5.8*F6,ЕСЛИ(F6>10,4.5*F6))
        # F6 - объем
        if unloading:
            if volume < 10:
                unloading_cost = 5.8 * volume
            else:
                unloading_cost = 4.5 * volume
        else:
            unloading_cost = 0
        
        # УПАКОВКА
        # Формула из Excel: =ЕСЛИ(H2=1,F6/0.3*3,ЕСЛИ(H2=2,F6/0.3*5,ЕСЛИ(H2=3,F6/0.3*7,ЕСЛИ(H2=4,F6/1*35,ЕСЛИ(H2=5,F6/1*85)))))
        # H2 - тип упаковки, F6 - объем
        packaging_costs = {
            'Мешок': (volume / 0.3) * 3,
            'Картонные уголки': (volume / 0.3) * 5,
            'Деревянная обрешетка': (volume / 0.3) * 7,
            'Паллет': (volume / 1) * 35,
            'Деревянный ящик': (volume / 1) * 85
        }
        
        packaging_cost = packaging_costs.get(packaging, 0)
        
        # КОМИССИЯ (остается как была)
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
        
        # ИТОГО
        # Формула из Excel: =F22+F24+F20+H16
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
        return jsonify({'error': 'Ошибка при расчете стоимости'}), 500

# Экспорт для Vercel
application = app

if __name__ == "__main__":
    app.run()