
# Imports
from flask import Flask, render_template, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
import os
import ffmpeg
import subprocess
import tempfile
from datetime import datetime

# Configuração do Flask
app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024  # 300MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

# Extensões permitidas
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_video_duration(filename):
    try:
        probe = ffmpeg.probe(filename)
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

def convert_to_gif(input_path, output_path, max_width=480, max_height=None):
    try:
        probe = ffmpeg.probe(input_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        orig_width = int(video_info['width'])
        orig_height = int(video_info['height'])
        # Ajusta proporção mantendo altura se max_height for passado
        if max_width and max_height:
            width, height = max_width, max_height
        elif max_width:
            if orig_width > max_width:
                height = int(orig_height * (max_width / orig_width))
                width = max_width
            else:
                width, height = orig_width, orig_height
        else:
            width, height = orig_width, orig_height
        palette_path = os.path.join(tempfile.gettempdir(), f'palette_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png')
        # Gerar a paleta
        palette_cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', f'fps=15,scale={width}:{height}:flags=lanczos,palettegen',
            palette_path
        ]
        result_palette = subprocess.run(palette_cmd, capture_output=True)
        if result_palette.returncode != 0:
            print('[convert_to_gif] Erro ao gerar paleta:', result_palette.stderr.decode())
            return False
        # Gerar o GIF usando a paleta
        gif_cmd = [
            'ffmpeg', '-y', '-i', input_path, '-i', palette_path,
            '-filter_complex', f'fps=15,scale={width}:{height}:flags=lanczos[x];[x][1:v]paletteuse',
            output_path
        ]
        result_gif = subprocess.run(gif_cmd, capture_output=True)
        if result_gif.returncode != 0:
            print('[convert_to_gif] Erro ao gerar GIF:', result_gif.stderr.decode())
            return False
        if os.path.exists(palette_path):
            os.remove(palette_path)
        return True
    except Exception as e:
        print(f"[convert_to_gif] Erro inesperado: {e}")
        return False

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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

    # Receber resolução do formulário
    resolution = request.form.get('resolution', '480x270')
    try:
        width, height = map(int, resolution.split('x'))
    except Exception:
        width, height = 480, 270

    gif_filename = f"{os.path.splitext(filename)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif"
    output_path = os.path.join(temp_dir, gif_filename)
    success = convert_to_gif(input_path, output_path, max_width=width, max_height=height)
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

# Inicialização do Flask
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)