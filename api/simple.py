from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>China Level Calculator</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h1>Калькулятор доставки China Level</h1>
        <p>Веб-приложение работает!</p>
        <div id="calculator">
            <h2>Расчет стоимости доставки</h2>
            <form id="delivery-form">
                <div>
                    <label>Категория товара:</label>
                    <select id="category">
                        <option value="Обычные товары">Обычные товары</option>
                        <option value="Одежда">Одежда</option>
                        <option value="Обувь">Обувь</option>
                    </select>
                </div>
                <div>
                    <label>Стоимость товара (₽):</label>
                    <input type="number" id="product-cost" required>
                </div>
                <div>
                    <label>Объем (м³):</label>
                    <input type="number" step="0.01" id="volume" required>
                </div>
                <div>
                    <label>Вес (кг):</label>
                    <input type="number" step="0.1" id="weight" required>
                </div>
                <div>
                    <label>Упаковка:</label>
                    <select id="packaging">
                        <option value="Мешок">Мешок (5$)</option>
                        <option value="Картонные уголки">Картонные уголки (6$/0.3м³)</option>
                        <option value="Деревянная обрешетка">Деревянная обрешетка (8$/0.3м³)</option>
                        <option value="Паллет">Паллет (35$/м³)</option>
                        <option value="Деревянный ящик">Деревянный ящик (100$/м³)</option>
                    </select>
                </div>
                <div>
                    <label>Скорость доставки:</label>
                    <select id="delivery-speed">
                        <option value="Стандартная (15-20 дней)">Стандартная (15-20 дней)</option>
                        <option value="Ускоренная (10-12 дней)">Ускоренная (10-12 дней) +30%</option>
                        <option value="Экспресс (5-7 дней)">Экспресс (5-7 дней) +80%</option>
                    </select>
                </div>
                <div>
                    <input type="checkbox" id="insurance">
                    <label for="insurance">Страховка (1% от стоимости)</label>
                </div>
                <div>
                    <input type="checkbox" id="unloading">
                    <label for="unloading">Разгрузка</label>
                </div>
                <button type="submit">Рассчитать</button>
            </form>
            <div id="result" style="display:none; margin-top:20px; padding:20px; background:#f0f0f0;">
                <h3>Результат расчета:</h3>
                <div id="result-content"></div>
            </div>
        </div>
        
        <script>
        document.getElementById('delivery-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                category: document.getElementById('category').value,
                product_cost: parseFloat(document.getElementById('product-cost').value) || 0,
                volume: parseFloat(document.getElementById('volume').value) || 0,
                weight: parseFloat(document.getElementById('weight').value) || 0,
                packaging: document.getElementById('packaging').value,
                delivery_speed: document.getElementById('delivery-speed').value,
                insurance: document.getElementById('insurance').checked,
                unloading: document.getElementById('unloading').checked
            };
            
            try {
                const response = await fetch('/calculate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    alert('Ошибка: ' + result.error);
                    return;
                }
                
                document.getElementById('result-content').innerHTML = `
                    <p><strong>Стоимость доставки:</strong> ${result.delivery_cost} ₽</p>
                    <p><strong>Упаковка:</strong> ${result.packaging_cost} ₽</p>
                    <p><strong>Страховка:</strong> ${result.insurance_cost} ₽</p>
                    <p><strong>Разгрузка:</strong> ${result.unloading_cost} ₽</p>
                    <p><strong>Комиссия (${result.commission_rate}):</strong> ${result.commission} ₽</p>
                    <p><strong>Плотность:</strong> ${result.density} кг/м³</p>
                    <hr>
                    <p><strong>ИТОГО:</strong> ${result.total_cost} ₽</p>
                `;
                
                document.getElementById('result').style.display = 'block';
                
            } catch (error) {
                alert('Ошибка при расчете: ' + error.message);
            }
        });
        </script>
    </body>
    </html>
    '''

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
        return jsonify({'error': f'Ошибка при расчете: {str(e)}'}), 500

# Экспорт для Vercel
application = app

if __name__ == "__main__":
    app.run()
