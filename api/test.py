from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from Vercel!", "status": "working"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Экспорт для Vercel
application = app

if __name__ == "__main__":
    app.run()
