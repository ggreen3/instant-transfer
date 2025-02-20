from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()  # Random secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    # Add a timestamp to the message
    timestamp = datetime.now().strftime("%H:%M:%S")
    decoded_msg = dna_decode(msg['encoded'])  # Decode the DNA message
    send({
        'message': decoded_msg,
        'timestamp': timestamp,
        'encoded': msg['encoded']  # Send the encoded DNA sequence back
    }, broadcast=True)

def dna_encode(text):
    # Simple DNA encoding: A=00, T=01, C=10, G=11
    dna_map = {'A': '00', 'T': '01', 'C': '10', 'G': '11'}
    binary = ''.join(format(ord(char), '08b') for char in text)
    dna = ''.join([dna_map[list(dna_map.keys())[int(binary[i:i+2], 2)] for i in range(0, len(binary), 2)])
    return dna

def dna_decode(dna):
    # Simple DNA decoding: A=00, T=01, C=10, G=11
    dna_map = {'00': 'A', '01': 'T', '10': 'C', '11': 'G'}
    binary = ''.join([dna_map[dna[i:i+2]] for i in range(0, len(dna), 2)])
    text = ''.join([chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)])
    return text

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return f"File {file.filename} uploaded successfully", 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
