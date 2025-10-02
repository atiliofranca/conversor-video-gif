
from flask import Flask, render_template, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
import os
import ffmpeg
import subprocess
import tempfile
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024  # 300MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_video_duration(filename):
    try:
        probe = ffmpeg.probe(filename)
        # Seleciona a primeira stream de vídeo
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        if video_stream and 'duration' in video_stream:
            duration = float(video_stream['duration'])
            return duration
        else:
            print('Não foi possível encontrar a duração do vídeo.')
            return None
    except ffmpeg.Error as e:
        print(f'Error: {str(e)}')
        return None

def convert_to_gif(input_path, output_path, max_width=480):
    print(f"[convert_to_gif] input_path: {input_path}")
    print(f"[convert_to_gif] output_path: {output_path}")
    try:
        probe = ffmpeg.probe(input_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        print(f"[convert_to_gif] original size: {width}x{height}")
        if width > max_width:
            height = int(height * (max_width / width))
            width = max_width
        print(f"[convert_to_gif] resized to: {width}x{height}")
        palette_path = os.path.join(tempfile.gettempdir(), f'palette_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png')
        print(f"[convert_to_gif] palette_path: {palette_path}")
        # Gerar a paleta
        palette_cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', f'fps=15,scale={width}:{height}:flags=lanczos,palettegen',
            palette_path
        ]
        print(f"[convert_to_gif] palette_cmd: {' '.join(palette_cmd)}")
        result_palette = subprocess.run(palette_cmd, capture_output=True)
        if result_palette.returncode != 0:
            print('[convert_to_gif] Erro ao gerar paleta:', result_palette.stderr.decode())
            return False
        print("[convert_to_gif] Palette generated successfully.")
        # Gerar o GIF usando a paleta
        gif_cmd = [
            'ffmpeg', '-y', '-i', input_path, '-i', palette_path,
            '-filter_complex', f'fps=15,scale={width}:{height}:flags=lanczos[x];[x][1:v]paletteuse',
            output_path
        ]
        print(f"[convert_to_gif] gif_cmd: {' '.join(gif_cmd)}")
        result_gif = subprocess.run(gif_cmd, capture_output=True)
        if result_gif.returncode != 0:
            print('[convert_to_gif] Erro ao gerar GIF:', result_gif.stderr.decode())
            return False
        print(f"[convert_to_gif] GIF salvo em: {output_path}")
        if os.path.exists(palette_path):
            os.remove(palette_path)
        return True
    except Exception as e:
        print(f"[convert_to_gif] Erro inesperado: {e}")
        return False

@app.route('/upload', methods=['POST'])
def upload_file():
    print('Campos recebidos:', list(request.files.keys()))
    file = request.files.get('file') or request.files.get('video')
    if not file:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

    filename = secure_filename(file.filename)
    temp_dir = tempfile.gettempdir()
    input_path = os.path.join(temp_dir, filename)
    file.save(input_path)

    duration = get_video_duration(input_path)
    if duration is None:
        return jsonify({'error': 'Não foi possível ler o arquivo de vídeo'}), 400
    if duration > 180:  # 3 minutos
        return jsonify({'error': 'O vídeo deve ter no máximo 3 minutos'}), 400

    gif_filename = f"{os.path.splitext(filename)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif"
    output_path = os.path.join(temp_dir, gif_filename)
    success = convert_to_gif(input_path, output_path)
    if not success:
        return jsonify({'error': 'Falha na conversão para GIF'}), 500

    try:
        response = make_response(send_file(
            output_path,
            mimetype='image/gif',
            as_attachment=True,
            download_name=gif_filename
        ))
        response.headers['Content-Type'] = 'image/gif'
        return response
    except Exception as e:
        return jsonify({'error': 'Erro ao enviar o arquivo GIF'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Arquivo muito grande. Tamanho máximo permitido: 300MB'}), 413

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Página não encontrada'}), 404

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)