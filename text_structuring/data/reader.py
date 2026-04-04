from docx import Document

def reader(file_name:str) -> str:
    """Возвращает чистый текст из .docx файла или .txt"""
    if file_name.split('.')[-1] == 'docx':
        doc = Document(file_name)
        return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    else:
        with open(file_name, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()

