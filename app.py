import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# Validate required vars
required_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB']
for var in required_vars:
    if not app.config.get(var):
        raise RuntimeError(f"Missing MySQL environment variable: {var}")

mysql = MySQL(app)

def init_db():
    cur = mysql.connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT NOT NULL
        );
    """)
    mysql.connection.commit()
    cur.close()

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages ORDER BY id DESC')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')

    if not new_message or not new_message.strip():
        return jsonify({"error": "Message cannot be empty"}), 400

    cur = mysql.connection.cursor()
    cur.execute(
        'INSERT INTO messages (message) VALUES (%s)',
        (new_message,)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': new_message})

if __name__ == '__main__':
    # ✅ THIS is the critical fix
    with app.app_context():
        init_db()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv("FLASK_DEBUG") == "1"
    )
