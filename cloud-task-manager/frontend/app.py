from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:5000')


@app.route('/')
def index():
    try:
        response = requests.get(f'{BACKEND_URL}/tasks', timeout=5)
        tasks = response.json()
    except Exception as e:
        tasks = []
        print(f"Error contacting backend: {e}")
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    if title:
        try:
            requests.post(
                f'{BACKEND_URL}/tasks',
                json={'title': title, 'description': description},
                timeout=5
            )
        except Exception as e:
            print(f"Error adding task: {e}")
    return redirect(url_for('index'))


@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    try:
        requests.put(f'{BACKEND_URL}/tasks/{task_id}', json={}, timeout=5)
    except Exception as e:
        print(f"Error toggling task: {e}")
    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    try:
        requests.delete(f'{BACKEND_URL}/tasks/{task_id}', timeout=5)
    except Exception as e:
        print(f"Error deleting task: {e}")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
