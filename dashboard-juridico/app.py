from flask import Flask, render_template, request, jsonify, send_from_directory
import PyPDF2
import markdown
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'pdf', 'md', 'markdown'}

# Criar pasta uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_pdf_text(filepath):
    """Extrai texto de PDF"""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Erro ao ler PDF: {str(e)}"

def read_markdown(filepath):
    """Lê arquivo Markdown"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Erro ao ler Markdown: {str(e)}"

def parse_laudo(text):
    """Extrai informações chave do laudo"""
    data = {
        'placa': '',
        'valor_aprovado': '',
        'participacao': '',
        'economia': '',
        'status': 'Pendente',
        'data_analise': datetime.now().strftime('%d/%m/%Y'),
        'documentos_pendentes': []
    }
    
    # Buscar informações no texto
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'Placa' in line and i+1 < len(lines):
            data['placa'] = lines[i+1].strip()
        elif 'VALOR APROVADO' in line:
            parts = line.split(':')
            if len(parts) > 1:
                data['valor_aprovado'] = parts[1].strip()
        elif 'PARTICIPAÇÃO' in line or 'Participação' in line:
            parts = line.split(':')
            if len(parts) > 1:
                data['participacao'] = parts[1].strip()
        elif 'ECONOMIA' in line or 'Economia' in line:
            parts = line.split(':')
            if len(parts) > 1:
                data['economia'] = parts[1].strip()
        elif 'CNH' in line and 'NÃO APRESENTADA' in line:
            data['documentos_pendentes'].append('CNH do condutor')
        elif 'CRLV' in line and 'NÃO APRESENTADO' in line:
            data['documentos_pendentes'].append('CRLV 2025')
    
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Processar arquivo
        ext = filename.rsplit('.', 1)[1].lower()
        
        if ext == 'pdf':
            content = extract_pdf_text(filepath)
        else:  # markdown
            content = read_markdown(filepath)
        
        # Converter markdown para HTML se necessário
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        
        # Extrair dados do laudo
        laudo_data = parse_laudo(content)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content': html_content,
            'laudo_data': laudo_data
        })
    
    return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

@app.route('/approve', methods=['POST'])
def approve():
    data = request.json
    decisao = data.get('decisao')
    observacoes = data.get('observacoes', '')
    filename = data.get('filename')
    
    # Aqui você salvaria a decisão em banco de dados
    # Por enquanto, apenas retornamos sucesso
    
    return jsonify({
        'success': True,
        'message': f'Laudo {decisao} com sucesso!',
        'decisao': decisao,
        'data': datetime.now().strftime('%d/%m/%Y %H:%M')
    })

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
