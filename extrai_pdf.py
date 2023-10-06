import os
from PyPDF2 import PdfReader

# Pasta contendo os arquivos PDF
pasta_pdf = 'C:\\Users\\Axxen\\Desktop\\script_marcela'

# Pasta de saída para os arquivos TXT
pasta_saida = 'C:\\Users\\Axxen\\Desktop\\script_marcela'

# Certifique-se de que a pasta de saída existe
if not os.path.exists(pasta_saida):
    os.makedirs(pasta_saida)

# Função para extrair texto de um arquivo PDF
def extrair_texto_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        num_paginas = len(pdf_reader.pages)  # Usando len(reader.pages) para obter o número de páginas
        texto_completo = ''

        for pagina_num in range(num_paginas):
            pagina = pdf_reader.pages[pagina_num]
            texto_pagina = pagina.extract_text()
            texto_completo += texto_pagina

        return texto_completo

# Processar todos os arquivos PDF na pasta de entrada
for arquivo_pdf in os.listdir(pasta_pdf):
    if arquivo_pdf.endswith('.pdf'):
        pdf_path = os.path.join(pasta_pdf, arquivo_pdf)
        texto = extrair_texto_pdf(pdf_path)

        # Salvar o texto em um arquivo TXT na pasta de saída
        nome_arquivo_txt = os.path.splitext(arquivo_pdf)[0] + '.txt'
        caminho_arquivo_txt = os.path.join(pasta_saida, nome_arquivo_txt)

        with open(caminho_arquivo_txt, 'w', encoding='utf-8') as txt_file:
            txt_file.write(texto)

print('Conversão concluída!')
