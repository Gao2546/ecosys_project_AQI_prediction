import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/app/images'  # ตรวจสอบว่าโฟลเดอร์นี้มีอยู่
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# สร้างโฟลเดอร์ถ้ายังไม่มี
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/success', methods = ['POST'])   
def success():   
    if request.method == 'POST':   
        f = request.files['file'] 
        f.save(f.filename) 

@app.route('/media/upload', methods=['POST'])
def upload_media():
    if 'file' not in request.files:
        return jsonify({'error': 'media not provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'no file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'file type not allowed'}), 400
    filename = secure_filename(file.filename)
    
    # บันทึกไฟล์ลงในโฟลเดอร์
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # ตรวจสอบว่าไฟล์ถูกบันทึกสำเร็จ
    if os.path.exists(file_path):
        return jsonify({'msg': 'media uploaded successfully', 'path': file_path})
    else:
        return jsonify({'error': 'file save failed'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
