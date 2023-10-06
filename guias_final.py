from typing import Tuple, Any

import fitz
import os
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from openpyxl import Workbook
from openpyxl import load_workbook
from glob import glob

files = glob('*pdf')
files = [f for f in files if not f.startswith('~$')]


fazenda = {
    'cnpj': r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
    'razao_social': r'NOME/TELEFONE\n([^\-]*)',
    'valor': r'VALOR TOTAL\s*([\d.,]+)'
}

receita = {
    'cnpj': r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
    'razao_social': r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\n([^\n]+?)\n',
    'valor':  r'Valor Total do Documento\n([\d.]+,\d{2})'
}

documentos_regexes = {
    r'\nMINISTÉRIO DA FAZENDA\n': fazenda,
    r'Composição do Documento de Arrecadação': receita
}

def extrai_valores(texto:str, regexes:dict) -> tuple[Any, Any, Any]:
    resultados = []
    for label, pattern in regexes.items():
        match = re.search(pattern, texto)
        valor = match.group(1)
        valor = valor if valor else ''
        resultados.append(valor)

    cnpj, receita, valor = resultados
    return cnpj, receita, valor

def extrai_texto(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        return texto
    except Exception as e:
        print(f"Erro ao extrair informações do PDF: {str(e)}")
        return ''

def parse_pdf(pdf_path):
    texto = extrai_texto(pdf_path)
    for key, regexes in documentos_regexes.items():
        m = re.search(key, texto)
        if m:
            valores = extrai_valores(texto, regexes)
            return valores
    return "", "", 0.0






# def extrair_valores_cnpj_razao_social_e_valor_total(pdf_path):
#     try:
#         doc = fitz.open(pdf_path)
#         texto = ""
#         for pagina in doc:
#             texto += pagina.get_text()
#
#
#         cnpj_pattern = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
#         match_cnpj = re.search(cnpj_pattern, texto)
#         cnpj = match_cnpj.group() if match_cnpj else ''
#
#
#         razao_social_pattern1 = r'NOME/TELEFONE\n(.+?)\n'
#         match_razao_social1 = re.search(razao_social_pattern1, texto)
#         razao_social1 = match_razao_social1.group(1).strip().split(' - ')[0] if match_razao_social1 else ''
#
#
#         razao_social_pattern2 = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\n(.+?)\n'
#         match_razao_social2 = re.search(razao_social_pattern2, texto)
#         razao_social2 = match_razao_social2.group(1).strip() if match_razao_social2 else ''
#
#
#         razao_social = razao_social1 if razao_social1 else razao_social2
#
#
#         valor_total_pattern1 = r'VALOR TOTAL\s*([\d.,]+)'
#         match_valor_total1 = re.search(valor_total_pattern1, texto)
#         valor_total1 = match_valor_total1.group(1).replace(',', '') if match_valor_total1 else '0.0'
#
#
#         valor_total_pattern2 = r'Valor Total do Documento\n([\d.]+,\d{2})'
#         match_valor_total2 = re.search(valor_total_pattern2, texto, re.IGNORECASE)
#         valor_total2 = match_valor_total2.group(1).replace('.', '').replace(',', '.') if match_valor_total2 else '0.0'
#
#
#         valor_total = valor_total1 if valor_total1 else valor_total2
#
#         return cnpj, razao_social, float(valor_total.replace(',', '.'))
#
#
#     except Exception as e:
#         print(f"Erro ao extrair informações do PDF: {str(e)}")
#         return "", "", 0.0







def iniciar_extracao():
    global pasta_pdf
    pasta_pdf = pasta_entry.get()
    pasta_label.config(text=f"Pasta com PDFs: {pasta_pdf}")

    informacoes_pdf.clear()
    for arquivo in os.listdir(pasta_pdf):
        if arquivo.endswith('.pdf') and not arquivo.startswith('~$'):
            pdf_path = os.path.join(pasta_pdf, arquivo)
            #cnpj, razao_social, valor_total = extrair_valores_cnpj_razao_social_e_valor_total(pdf_path)
            cnpj, razao_social,valor_total = parse_pdf(pdf_path)
            informacoes_pdf.append([arquivo, cnpj, razao_social, valor_total])


    print("Informações PDF:")
    print(informacoes_pdf)
    print("Colunas:")
    print(colunas)


    df = pd.DataFrame(informacoes_pdf, columns=colunas)
    df['Valor Total'] = df['Valor Total'].apply(lambda valor: float(valor.replace(".", "").replace(",", ".")))

    nome_arquivo_excel = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                      filetypes=[("Arquivos Excel", "*.xlsx")])

    if nome_arquivo_excel:

        df.to_excel(nome_arquivo_excel, index=False, engine='openpyxl')


        wb = load_workbook(nome_arquivo_excel)
        ws = wb.active


        for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
            cell = row[0]
            nome_arquivo = cell.value
            if nome_arquivo:
                caminho_completo = os.path.join(pasta_pdf, nome_arquivo)
                cell.hyperlink = caminho_completo
                cell.style = "Hyperlink"


        wb.save(nome_arquivo_excel)

        resultado_label.config(text=f'Valores extraídos e salvos em "{nome_arquivo_excel}".')


root = tk.Tk()
root.title("Extração de CNPJ, Razão Social e Valor Total de PDFs")


instrucoes_label = tk.Label(root, text="Informe o diretório:")
pasta_label = tk.Label(root, text="Pasta com PDFs não selecionada.")
pasta_entry = tk.Entry(root, width=50)
selecionar_button = tk.Button(root, text="Selecionar Pasta",
                              command=lambda: pasta_entry.insert(0, filedialog.askdirectory()))
iniciar_button = tk.Button(root, text="Iniciar Extração", command=iniciar_extracao)
resultado_label = tk.Label(root, text="")


instrucoes_label.pack()
pasta_entry.pack()
selecionar_button.pack()
pasta_label.pack()
iniciar_button.pack()
resultado_label.pack()


informacoes_pdf = []


colunas = ["Nome do Arquivo", "CNPJ", "Razão Social", "Valor Total"]


root.mainloop()
