import pdfplumber
import pandas as pd
import re
import unicodedata
import io

def normalize_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text.upper().strip()

def limpar_agente(texto):
    texto = re.sub(r"\bT\b\s*\d+,\d{2}\s*\d+,\d{2}", "", texto)
    texto = re.sub(r"\s{2,}", " ", texto)
    return texto.strip()

def limpar_historico(documento, agente):
    """Remove numeros e caracteres especiais do inicio para deixar o historico limpo"""
    # Remove numeros, hifens, pontos e espacos do inicio (muito agressivo)
    doc_limpo = re.sub(r"^[\d\s\-\.]+", "", str(documento)).strip()
    agente_limpo = re.sub(r"^[\d\s\-\.]+", "", str(agente)).strip()
    
    # Se ainda tiver numeros no inicio, remove novamente
    doc_limpo = re.sub(r"^\d+\s*-?\s*", "", doc_limpo).strip()
    agente_limpo = re.sub(r"^\d+\s*-?\s*", "", agente_limpo).strip()
    
    # Se ficou vazio, mantem o original
    if not doc_limpo:
        doc_limpo = str(documento).strip()
    if not agente_limpo:
        agente_limpo = str(agente).strip()
    
    return doc_limpo, agente_limpo

# ========== LISTAS DE CODIGOS ==========

codes_salario = ["136", "3571", "9372", "3451", "3799", "3206", "3171", "3732", "3755", "3025", "3331", "2793", "1194", "85", "2625", "2556", "2780", "3059", "3099", "2125", "1413", "2763", "2097", "2563", "3972", "4232"]
codes_passagem = ["1084", "1729"]
codes_impostos = ["237", "360"]
codes_seguros = ["1689", "2532"]
codes_fornecedores_extra = ["1253", "1288", "458", "2568", "3947", "2086", "3523", "1960", "75", "3975", "316", "3174", "1334", "1403", "1421", "1439", "1619", "1990", "3369", "3613", "1930", "2698", "4142", "621", "3585", "3245", "622", "4281", "4339", "4207"]
codes_frete = ["1397", "3702"]

# ========== MAPEAMENTO POR PALAVRAS-CHAVE ==========

mapeamento = {
    "SABESP": ("53118-0", "CONSUMO DE AGUA"),
    "AGUA": ("53118-0", "CONSUMO DE AGUA"),
    "JAGUARI": ("53117-6", "CONSUMO DE ENERGIA"),
    "ENERGIA": ("53117-6", "CONSUMO DE ENERGIA"),
    "CPFL": ("53117-6", "CONSUMO DE ENERGIA"),
    "TELEFONICA": ("53267", "TELEFONE"),
    "VIVO": ("53267", "TELEFONE"),
    "INTERNET": ("53281", "INTERNET"),
    "SEM PARAR": ("53178", "PEDAGIO / SEM PARAR"),
    "PEDAGIO": ("53178", "PEDAGIO / SEM PARAR"),
    "JUROS": ("55105", "JUROS E MULTAS"),
    "MULTA": ("58101-4", "MULTA P/INFRACOES"),
    "SEGURO": ("53165-5", "SEGUROS GERAIS"),
    "RDV": ("53143-9", "DESPESAS DE VIAGEM"),
    "ADIANT": ("11154-0", "ADIANTAMENTO DE VIAGEM"),
    "ADIANTAMENTO": ("11154-0", "ADIANTAMENTO DE VIAGEM"),
    "LICENCIAMENTO": ("53149-6", "LICENCIAMENTO DE VEICULOS"),
    "IPVA": ("53099-1", "IMPOSTOS E TAXAS"),
    "SALARIO": ("53163-6", "SALARIOS E ORDENADOS"),
    "CORREIO": ("53136-6", "DESPESAS POSTAIS"),
    "UNIMED": ("53125-0", "PLANO DE SAUDE"),
    "FRETE": ("53119-3", "FRETES E CARRETOS"),
    "EMPRESTIMO": ("21203", "EMPRESTIMO - BANCO DO BRASIL"),
    "ITAU": ("21204", "EMPRESTIMO - ITAU"),
    "SANTANDER": ("21202", "EMPRESTIMO - SANTANDER"),
    "FATURAS": ("04297", "FATURAS"),
    "PRO-LABORE": ("21022-8", "PRO-LABORE"),
    "SERASA": ("53162", "SERASA"),
    "FINANCIAMENTO": ("21204-5", "FINANCIAMENTO"),
    "LUCROS": ("21823-4", "LUCROS"),
}

# ========== DICIONARIO DE FORNECEDORES ==========

dic_fornecedores = {
    "SOLUCAO QUIMICA": "170986",
    "SUPERMERCADO BOTELHO": "008846",
    "METALURGICA RIO PARDO": "051741",
    "DIAS VENANZONI": "000143",
    "ACOS SANTA CRUZ": "155852",
    "GONCALVES COMERCIAL DE GLP": "090187",
    "AUTO POSTO THATHIMA": "000471",
    "MADEIREIRA LIMA": "133307",
    "ACOS SAO CARLOS": "80224",
    "PACKPEL EMBALAGENS": "190322",
    "MAGRAF ALMEIDA E RAMOS": "035961",
    "MARCHIORI LOURENCO": "155869",
    "SCHEM DAS AMERICAS": "140772",
    "CARMOCAL DO BRASIL": "178760",
    "VUOLO E CIA": "000002",
    "FLAVIO LUBRIFICANTES": "087007",
    "BRENNTAG QUIMICA": "077429",
    "RODONAVES TRANSPORTES": "010969",
    "GV8 WEB SITES": "103185",
    "RINALDO ANDRADE REZENDE": "098217",
    "ALELO S.A.": "083395",
    "CEDNET": "057457",
    "JC MONTEIRO MAQUINAS": "201680",
    "CELIO CHRISTONI": "184812",
    "ARCELORMITTAL": "102105",
    "CIBELE S. S. MORINI": "155852",
    "FABIO LUIZ GOZZO": "36073",
    "STOKE LIVRARIA": "000239",
    "PELLEGATTI": "114905",
    "CASA AVENIDA": "154452",
    "CONSTRUTORMIX": "083891",
    "DEGAM EMBALAGENS": "116428",
    "THERMO GASES": "182510",
    "PLASTICOS MAGNO": "140220",
    "BSC QUIMICA": "166110",
    "RECALL COM DE PECAS": "008729",
    "SAEMVIG": "201661",
    "GENERAL MASTER": "144754",
    "GOLPACK": "130248",
    "NAGEL MONITORAMENTO": "79466",
    "COMERCIAL SANCHES MARIN": "000042",
    "PLURY QUIMICA": "201669",
    "MANUCHAR": "142365",
    "QUIMICA ANASTACIO": "143150",
    "ACADIAN DO BRASIL": "198608",
    "COOPERATIVA TERRA IDEAL": "188755",
    "MRP MOTORES": "147701",
    "MAIS DISTRIBUIDORA": "2011",
    "CTR SOLUCOES AMBIENTAIS": "3098",
    "FERTIPAR BANDEIRANTES": "3997",
    "AGROTIS AGROINFORMATICA": "70",
    "PRO VIDA OCUPACIONAL": "1828",
    "LAJES E BLOCOS TAPAJOS": "4262",
    "NICROM QUIMICA": "2469",
    "JOCA TRUCK COM PNEUS": "942",
    "EXPRESSO SAO MIGUEL": "2408",
    "SAO LUCAS COMBUSTIVEIS": "4172",
    "COMERCIO ROMANO": "3951",
    "E.K.C DA FONSECA": "4076",
    "FARDAS EXPRESS": "3213",
    "LTFLEX": "3776",
    "EBAZAR.COM.BR": "3071",
    "MERCADO LIVRE": "2229",
    "CORREA MATERIAIS ELETRICOS": "3994",
    "BORDALASER BORDADOS": "3175",
    "ALVES MORAES PRE FABRICADOS": "3774",
    "N.S PRE FABRICADOS": "4206",
    "SEU ECOMMERCE": "4104",
    "SONODA INFORMATICA": "3339",
    "PRIMO PIGA E CIA": "934",
    "UPEXPRESS UNIFORMES": "4208",
    "MALVAGLIA COMERCIAL": "4224",
    "PIRES EMBALAGENS": "4312",
    "PARAFUSOS E TAL": "4031",
    "GRAFICA ITAUNA": "563",
    "RADIADORES AMANTINI": "3592",
    "MELACOS BRASILEIROS": "2787",
    "MULTITECNICA INDUSTRIAL": "2597",
    "L L LUBRIFICANTES": "3685",
    "ASSIS DIESEL DE VEICULOS": "4197",
    "SANTOS E FRASSON PROJETOS": "4297",
    "LIMA MANUTENCOES": "3910",
    "AUTO PECAS SCHIAVETTI": "3920",
    "INDUSTRIA E COMERCIO DE CAFE": "2518",
    "UNIMED DE OURINHOS": "3040",
    "DIGI-TRON INSTRUMENTOS": "4211",
    "BALANCAS BAURU": "3478",
    "CARBON CHEMICALS": "3158",
    "ICL AMERICA DO SUL": "2586",
    "ACE ASSOCIACAO COMERCIAL": "71",
    "GB IMPORT SP": "4279",
    "PEGORER TEM COMERCIO": "521",
    "ATIAS MIHAEL COMERCIO": "3563",
    "LEANDRO ANASTACIO": "4134",
    "HIDROCERES COMERCIAL": "4",
    "T L BASSETTO COMERCIAL": "793",
    "GRABE BOMBAS": "3051",
    "GENS EXPRESS COMERCIO": "4284",
    "DAMOL COMERCIO DE AUTO": "266",
    "DONIZETI APARECIDO DE PAIVA": "3741",
    "JOSE CARLOS DE ALMEIDA FILHO": "4173",
    "AUTO MECANICA AMIGOS ALVES": "3466",
    "IZNEL INDUSTRIA E COMERCIO": "3192",
    "JOSIANE GOMES PEIXE": "4157",
    "DELLA FINA BONANI": "3964",
    "NZB COMERCIO DE EMBALAGENS": "2406",
    "LDM COMERCIO DE MAQUINAS": "4038",
    "ROMEU BRAZ PEREIRA NUNES": "4200",
    "MERKATO INDUSTRIA": "2749",
    "TOPVENDAS COMERCIO": "4041",
    "TUBASEG EQUIPAMENTOS": "3001",
    "MARANGONI E SOUZA COMERCIO": "4226",
    "FORMEDTEC COMERCIO": "4215",
    "JOAO PAULO MOLINA GOMES": "4227",
    "NAPOLI COMERCIO VAREJISTA": "3140",
    "M. CASSAB COMERCIO": "4199",
    "E J DE OLIVEIRA COMERCIO DE FERRO": "2551",
    "MINISA EQUIPAMENTOS": "4223",
    "COMERCIAL DE MATERIAIS": "1100",
    "PLASMASUL COMERCIO": "4202",
    "ITATIJUCA COMERCIO": "3362",
    "IBAMA": "3307",
    "FORTES COMERCIO": "4276",
    "ERCA INDUSTRIA E COMERCIO": "3242",
    "C. RENOFIO AUTO PECAS": "3287",
    "OTAVIO SCATAMBULO": "1111",
    "EMERSON GONCALVES FOTOGRAFIAS": "4102",
    "ANJO EQUIPAMENTOS RODOVIARIOS": "4186",
    "ELDES MIOTTO MENONI": "3973",
    "PRIMO PIGA E CIA": "934",
    "UPEXPRESS UNIFORMES": "4208",
    "MALVAGLIA COMERCIAL": "4224",
    "PIRES EMBALAGENS": "4312",
    "PARAFUSOS E TAL": "4031",
    "GRAFICA ITAUNA": "563",
    "RADIADORES AMANTINI": "3592",
    "MELACOS BRASILEIROS": "2787",
    "MULTITECNICA INDUSTRIAL": "2597",
    "L L LUBRIFICANTES": "3685",
    "ASSIS DIESEL DE VEICULOS": "4197",
    "SANTOS E FRASSON PROJETOS": "4297",
    "LIMA MANUTENCOES": "3910",
    "AUTO PECAS SCHIAVETTI": "3920",
    "INDUSTRIA E COMERCIO DE CAFE": "2518",
    "UNIMED DE OURINHOS": "3040",
    "DIGI-TRON INSTRUMENTOS": "4211",
    "BALANCAS BAURU": "3478",
    "CARBON CHEMICALS": "3158",
    "ICL AMERICA DO SUL": "2586",
    "ACE ASSOCIACAO COMERCIAL": "71",
    "GB IMPORT SP": "4279",
    "PEGORER TEM COMERCIO": "521",
    "ATIAS MIHAEL COMERCIO": "3563",
    "LEANDRO ANASTACIO": "4134",
    "HIDROCERES COMERCIAL": "4",
    "T L BASSETTO COMERCIAL": "793",
    "GRABE BOMBAS": "3051",
    "GENS EXPRESS COMERCIO": "4284",
    "DAMOL COMERCIO DE AUTO": "266",
    "DONIZETI APARECIDO DE PAIVA": "3741",
    "JOSE CARLOS DE ALMEIDA FILHO": "4173",
    "AUTO MECANICA AMIGOS ALVES": "3466",
    "IZNEL INDUSTRIA E COMERCIO": "3192",
    "JOSIANE GOMES PEIXE": "4157",
    "DELLA FINA BONANI": "3964",
    "NZB COMERCIO DE EMBALAGENS": "2406",
    "LDM COMERCIO DE MAQUINAS": "4038",
    "ROMEU BRAZ PEREIRA NUNES": "4200",
    "MERKATO INDUSTRIA": "2749",
    "TOPVENDAS COMERCIO": "4041",
    "TUBASEG EQUIPAMENTOS": "3001",
    "MARANGONI E SOUZA COMERCIO": "4226",
    "FORMEDTEC COMERCIO": "4215",
    "JOAO PAULO MOLINA GOMES": "4227",
    "NAPOLI COMERCIO VAREJISTA": "3140",
    "M. CASSAB COMERCIO": "4199",
    "E J DE OLIVEIRA COMERCIO DE FERRO": "2551",
    "MINISA EQUIPAMENTOS": "4223",
    "COMERCIAL DE MATERIAIS": "1100",
    "PLASMASUL COMERCIO": "4202",
    "ITATIJUCA COMERCIO": "3362",
    "IBAMA": "3307",
    "FORTES COMERCIO": "4276",
    "ERCA INDUSTRIA E COMERCIO": "3242",
    "C. RENOFIO AUTO PECAS": "3287",
    "OTAVIO SCATAMBULO": "1111",
    "EMERSON GONCALVES FOTOGRAFIAS": "4102",
    "ANJO EQUIPAMENTOS RODOVIARIOS": "4186",
    "ELDES MIOTTO MENONI": "3973",
    "MESTRE DA OBRA": "4213",
}

def classify_pagamento(agente, documento):
    """Classifica um lancamento de pagamento baseado em regras e retorna (conta_debito, nome_conta, terceiro)"""
    
    hist_norm = normalize_text(agente)
    doc_norm = normalize_text(documento)
    
    # Extrai codigo numerico do inicio do agente
    match_code = re.match(r'^(\d+)', hist_norm)
    code = match_code.group(1) if match_code else None
    
    # 1. Verificar codigos especificos de SALARIO
    if code in codes_salario:
        return "53163-6", "SALARIOS E ORDENADOS", ""
    
    # 2. Verificar codigos de IMPOSTOS
    if code in codes_impostos:
        return "53099-1", "IMPOSTOS E TAXAS", ""
    
    # 3. Verificar codigos de PASSAGEM
    if code in codes_passagem:
        return "53143-9", "DESPESAS DE VIAGEM", ""
    
    # 4. Verificar codigos de SEGUROS
    if code in codes_seguros:
        return "53165-5", "SEGUROS GERAIS", ""
    
    # 5. Verificar codigos de FRETE
    if code in codes_frete:
        return "53119-3", "FRETES E CARRETOS", ""
    
    # 6. Verificar codigos de FORNECEDORES EXTRA
    if code in codes_fornecedores_extra:
        return "04297", "FORNECEDORES", ""
    
    # 7. Verificar palavras-chave no historico (PRIORIDADE ALTA)
    for palavra, (conta, nome) in mapeamento.items():
        if palavra in hist_norm or palavra in doc_norm:
            return conta, nome, ""
    
    # 8. Verificar dicionario de fornecedores
    for fornecedor, codigo in dic_fornecedores.items():
        if fornecedor in hist_norm:
            return "04297", "FORNECEDORES", codigo
    
    # 9. Se for NF ou numero puro, classificar como fornecedor
    if "NF" in doc_norm or re.match(r'^\d+$', doc_norm):
        return "04297", "FORNECEDORES", ""
    
    # 10. Padrao: Classificacao Manual
    return "99999-9", "CLASSIFICACAO MANUAL", ""

# --- LOGICA DE PAGAMENTOS (v14) ---
def process_pagamentos(pdf_content, dic_terceiros):
    data_rows = []
    current_bank_code = "11203-0"
    
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            texto_pag = page.extract_text()
            if not texto_pag:
                continue
            
            # Detectar banco
            if "SANTANDER" in texto_pag.upper():
                current_bank_code = "11202"
            elif "BANCO DO BRASIL" in texto_pag.upper() or "BANCO BRASIL" in texto_pag.upper():
                current_bank_code = "11203-0"
            
            linhas = texto_pag.split("\n")
            
            for linha in linhas:
                linha = linha.strip()
                
                # Ignorar cabecalhos e linhas vazias
                if not linha or re.search(r"Emissao|Documento|Pagina|Total|Pagamentos|Data|Valor", linha, re.IGNORECASE):
                    continue
                
                # Procurar por data no inicio da linha
                datas = re.findall(r"\d{2}/\d{2}/\d{4}", linha)
                if not datas:
                    continue
                
                data_baixa = datas[0]
                
                # Procurar por valor monetario
                valor_match = re.search(r"\d{1,3}(\.\d{3})*,\d{2}", linha)
                if not valor_match:
                    continue
                
                valor_str = valor_match.group(0)
                
                try:
                    formatted_date = f"{data_baixa.split('/')[2]}-{data_baixa.split('/')[1]}-{data_baixa.split('/')[0]}"
                except:
                    formatted_date = data_baixa
                
                # Extrair documento e agente removendo data e valor
                linha_limpa = re.sub(r"\d{2}/\d{2}/\d{4}", "", linha).strip()
                linha_limpa = re.sub(r"\d{1,3}(\.\d{3})*,\d{2}", "", linha_limpa).strip()
                
                # Dividir em documento e agente
                partes = linha_limpa.split()
                
                if len(partes) >= 2:
                    documento = partes[0]
                    agente = " ".join(partes[1:]).strip()
                elif len(partes) == 1:
                    documento = partes[0]
                    agente = partes[0]
                else:
                    continue
                
                if agente:
                    # Classificar (usar dados originais para classificacao)
                    conta_debito, nome_conta, terceiro = classify_pagamento(agente, documento)
                    
                    # Limpar historico para exibicao
                    doc_limpo, agente_limpo = limpar_historico(documento, agente)
                    
                    data_rows.append({
                        "Data": formatted_date,
                        "Valor": f"R$ {valor_str}",
                        "Historico": f"{doc_limpo} - {agente_limpo}".strip(" -"),
                        "NomeConta": nome_conta,
                        "CONTA_DEBITO": conta_debito,
                        "CONTA_CREDITO": current_bank_code,
                        "TERCEIRO": terceiro,
                    })
    
    return pd.DataFrame(data_rows)

# --- LOGICA DE RECEBIMENTOS (v20) ---
def process_recebimentos(pdf_content):
    data_rows = []
    banco_detectado = "11203"  # Padrao: Banco do Brasil
    
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            texto_pag = page.extract_text()
            if not texto_pag: 
                continue
            
            # Detectar banco
            if re.search(r"BANCO DO BRASIL|BB\b", texto_pag, re.IGNORECASE): 
                banco_detectado = "11203"
            elif re.search(r"SANTANDER", texto_pag, re.IGNORECASE): 
                banco_detectado = "11202"
            
            linhas = texto_pag.split("\n")
            
            for linha in linhas:
                linha = linha.strip()
                
                # Ignorar cabecalhos
                if re.search(r"Emissao|Documento|Pagina|Total|Recebimentos", linha, re.IGNORECASE): 
                    continue
                
                # Extrair dados
                doc = re.search(r"\d+-\d+-\d+", linha)
                valor_match = re.search(r"\d{1,3}(\.\d{3})*,\d{2}", linha)
                datas = re.findall(r"\d{2}/\d{2}/\d{4}", linha)
                
                if not datas or not doc or not valor_match: 
                    continue
                
                data_baixa = datas[0]
                
                try: 
                    formatted_date = f"{data_baixa.split('/')[2]}-{data_baixa.split('/')[1]}-{data_baixa.split('/')[0]}"
                except: 
                    formatted_date = data_baixa
                
                # Extrair agente
                agente_bruto = linha.split(doc.group())[-1]
                agente_bruto = re.sub(re.escape(valor_match.group()), "", agente_bruto)
                agente = limpar_agente(agente_bruto)
                
                data_rows.append({
                    "Duplicata": doc.group(),
                    "Agente": agente,
                    "Data": formatted_date,
                    "Valor": f"R$ {valor_match.group()}",
                    "CONTA_DEBITO": banco_detectado,
                    "CONTA_CREDITO": "80224"
                })
    
    return pd.DataFrame(data_rows)