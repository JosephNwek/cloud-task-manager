from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

tasks = []
task_id_counter = 1


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)


@app.route('/tasks', methods=['POST'])
def create_task():
    global task_id_counter
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    new_task = {
        'id': task_id_counter,
        'title': data.get('title'),
        'description': data.get('description', ''),
        'completed': False
    }
    task_id_counter += 1
    tasks.append(new_task)
    return jsonify(new_task), 201


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json() or {}
    for task in tasks:
        if task['id'] == task_id:
            if 'completed' in data:
                task['completed'] = data['completed']
            else:
                task['completed'] = not task['completed']
            return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            tasks.remove(task)
            return jsonify({'message': 'Task deleted'})
    return jsonify({'error': 'Task not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
