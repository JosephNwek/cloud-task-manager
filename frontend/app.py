from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)
BACKEND_URL = 'http://backend:5000/tasks'

@app.route('/')
def index():
    tasks = requests.get(BACKEND_URL).json()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form['description']
    requests.post(BACKEND_URL, json={'title': title, 'description': description})
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
