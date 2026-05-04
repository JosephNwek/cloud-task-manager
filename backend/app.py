from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = []
task_id = 1

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    global task_id
    data = request.get_json()
    new_task = {
        'id': task_id,
        'title': data.get('title'),
        'description': data.get('description'),
        'completed': False
    }
    task_id += 1
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    for task in tasks:
        if task['id'] == id:
            task['completed'] = True
            return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    for task in tasks:
        if task['id'] == id:
            tasks.remove(task)
            return jsonify({'message': 'Task deleted'})
    return jsonify({'error': 'Task not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
