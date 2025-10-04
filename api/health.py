from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({"status": "healthy", "message": "China Level Calculator is working!"})

@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "service": "calculator"})

# Экспорт для Vercel
application = app

if __name__ == "__main__":
    app.run()
