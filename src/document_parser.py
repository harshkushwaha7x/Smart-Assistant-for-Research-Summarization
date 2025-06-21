import pdfplumber

def parse_document(uploaded_file):
    if uploaded_file.name.lower().endswith('.pdf'):
        with pdfplumber.open(uploaded_file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text
    elif uploaded_file.name.lower().endswith('.txt'):
        return uploaded_file.read().decode('utf-8')
    else:
        raise ValueError('Unsupported file type') 