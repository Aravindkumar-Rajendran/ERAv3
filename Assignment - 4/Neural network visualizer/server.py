from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_progress')
def get_progress():
    try:
        with open('static/training_progress.json', 'r') as f:
            progress = json.load(f)
        return jsonify(progress)
    except:
        return jsonify({'error': 'No progress data available'})

if __name__ == '__main__':
    app.run(debug=True) 