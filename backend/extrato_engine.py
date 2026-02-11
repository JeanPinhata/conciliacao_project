import pdfplumber
import pandas as pd
import re
import io
import unicodedata

def normalize_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text.upper().strip()

def limpar_historico(texto):
    """Remove numeros e caracteres especiais do inicio do historico"""
    texto = re.sub(r"^[\d\s\-\.]+", "", str(texto)).strip()
    texto = re.sub(r"^\d+\s*-?\s*", "", texto).strip()
    if not texto:
        texto = str(texto).strip()
    return texto

# ========== DICIONARIOS (COPIADOS DO engine.py) ==========

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
    "TRANSFERENCIA": ("11201-0", "BANCOS CONTA MOVIMENTO"),
    "COBRANCA": ("11201-0", "BANCOS CONTA MOVIMENTO"),
}

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
    "MESTRE DA OBRA": "4213",
}

def classify_extrato(descricao, favorecido=""):
    """Classifica um movimento de extrato e retorna (conta_debito, nome_conta, terceiro)"""
    
    hist_norm = normalize_text(descricao)
    favorecido_norm = normalize_text(favorecido)
    
    # 1. Verificar palavras-chave no historico (PRIORIDADE ALTA)
    for palavra, (conta, nome) in mapeamento.items():
        if palavra in hist_norm:
            return conta, nome, ""
    
    # 2. Verificar dicionario de fornecedores (no favorecido ou historico)
    for fornecedor, codigo in dic_fornecedores.items():
        if fornecedor in hist_norm or fornecedor in favorecido_norm:
            return "04297", "FORNECEDORES", codigo
    
    # 3. Padrao: Bancos
    return "11201-0", "BANCOS CONTA MOVIMENTO", ""

def detect_bank(texto):
    """Detecta qual banco é baseado no conteúdo do PDF"""
    texto_upper = texto.upper()
    
    if "BANCO DO BRASIL" in texto_upper or "BANCO BRASIL" in texto_upper:
        return "BB"
    elif "SANTANDER" in texto_upper:
        return "SANTANDER"
    elif "ITAU" in texto_upper or "ITAÚ" in texto_upper:
        return "ITAU"
    else:
        return "DESCONHECIDO"

def process_extrato_bb(pdf_content):
    """Processa extrato do Banco do Brasil"""
    data_rows = []
    
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if not texto:
                continue
            
            linhas = texto.split("\n")
            i = 0
            
            while i < len(linhas):
                linha = linhas[i].strip()
                i += 1
                
                # Ignorar linhas vazias e cabeçalhos
                if not linha or "Dt. balancete" in linha or "Saldo Anterior" in linha:
                    continue
                
                # Extrair data (DD/MM/YYYY)
                data_match = re.search(r"(\d{2}/\d{2}/\d{4})", linha)
                if not data_match:
                    continue
                
                data = data_match.group(1)
                
                # Extrair valor (pode ter ponto de milhar e vírgula decimal)
                valor_match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s+([CD])", linha)
                if not valor_match:
                    continue
                
                valor_str = valor_match.group(1)
                tipo = valor_match.group(2)  # C = Crédito, D = Débito
                
                # Extrair histórico
                historico = ""
                partes = linha.split()
                try:
                    idx_valor = None
                    for j, parte in enumerate(partes):
                        if valor_str.replace(".", "").replace(",", "") in parte.replace(".", "").replace(",", ""):
                            idx_valor = j
                            break
                    
                    if idx_valor and idx_valor > 3:
                        historico = " ".join(partes[3:idx_valor]).strip()
                except:
                    pass
                
                historico = limpar_historico(historico) if historico else "Operação Bancária"
                
                # Formatar data para YYYY-MM-DD
                try:
                    dia, mes, ano = data.split("/")
                    data_formatada = f"{ano}-{mes}-{dia}"
                except:
                    data_formatada = data
                
                # Verificar se há linha de baixo com informações adicionais (favorecido)
                favorecido = ""
                nome_conta = ""
                if i < len(linhas):
                    proxima_linha = linhas[i].strip()
                    # Se a próxima linha não contém data no formato DD/MM/YYYY, é informação adicional
                    if proxima_linha and not re.search(r"\d{2}/\d{2}/\d{4}", proxima_linha):
                        # Extrair nome do favorecido (última parte da linha, após hora)
                        partes_proxima = proxima_linha.split()
                        # Procurar por padrão HH:MM e pegar tudo depois
                        hora_match = re.search(r"\d{2}:\d{2}", proxima_linha)
                        if hora_match:
                            idx_hora = proxima_linha.find(hora_match.group(0))
                            favorecido = proxima_linha[idx_hora + 5:].strip()
                            i += 1
                        else:
                            # Se não tiver hora, pegar tudo
                            favorecido = proxima_linha
                            i += 1
                
                # Classificar
                conta_classificada, nome_conta, terceiro = classify_extrato(historico, favorecido)
                
                # Determinar contas baseado no tipo
                if tipo == "C":
                    conta_credito = "11201-0"
                    conta_debito = conta_classificada
                else:
                    conta_debito = "11201-0"
                    conta_credito = conta_classificada
                
                data_rows.append({
                    "Data": data_formatada,
                    "Historico": historico,
                    "FORNECEDOR": favorecido,
                    "NOME_CONTA": nome_conta,
                    "CONTA_CREDITO": conta_credito if tipo == "C" else "",
                    "CONTA_DEBITO": conta_debito if tipo == "D" else "",
                    "TERCEIRO": terceiro,
                })
    
    return pd.DataFrame(data_rows)

def process_extrato_santander(pdf_content):
    """Processa extrato do Santander"""
    data_rows = []
    
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if not texto:
                continue
            
            linhas = texto.split("\n")
            
            for linha in linhas:
                linha = linha.strip()
                
                # Ignorar linhas vazias e cabeçalhos
                if not linha or "Data" in linha or "Descrição" in linha or "SALDO EM" in linha:
                    continue
                
                # Extrair data (DD/MM)
                data_match = re.search(r"(\d{2}/\d{2})", linha)
                if not data_match:
                    continue
                
                data = data_match.group(1)
                
                # Extrair valor
                valor_match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})-?", linha)
                if not valor_match:
                    continue
                
                valor_str = valor_match.group(1)
                eh_debito = "-" in linha[linha.find(valor_str):linha.find(valor_str) + 20]
                
                # Extrair descrição
                descricao = re.sub(r"^\d{2}/\d{2}\s+", "", linha)
                descricao = re.sub(r"\d{1,3}(?:\.\d{3})*,\d{2}-?$", "", descricao).strip()
                descricao = limpar_historico(descricao) if descricao else "Operação Bancária"
                
                # Formatar data para YYYY-MM-DD
                from datetime import datetime
                ano_atual = datetime.now().year
                try:
                    dia, mes = data.split("/")
                    data_formatada = f"{ano_atual}-{mes}-{dia}"
                except:
                    data_formatada = data
                
                # Classificar
                conta_classificada, nome_conta, terceiro = classify_extrato(descricao)
                
                data_rows.append({
                    "Data": data_formatada,
                    "Historico": descricao,
                    "FORNECEDOR": "",
                    "NOME_CONTA": nome_conta,
                    "CONTA_CREDITO": "11202" if not eh_debito else "",
                    "CONTA_DEBITO": "11202" if eh_debito else "",
                    "TERCEIRO": terceiro,
                })
    
    return pd.DataFrame(data_rows)

def process_extrato_itau(pdf_content):
    """Processa extrato do Itaú"""
    data_rows = []
    
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if not texto:
                continue
            
            linhas = texto.split("\n")
            
            for linha in linhas:
                linha = linha.strip()
                
                # Ignorar linhas vazias e cabeçalhos
                if not linha or "Data" in linha or "Descrição" in linha or "SALDO APLIC" in linha:
                    continue
                
                # Extrair data (DD/MM)
                data_match = re.search(r"(\d{2}/\d{2})", linha)
                if not data_match:
                    continue
                
                data = data_match.group(1)
                
                # Extrair valor
                valor_match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})-?", linha)
                if not valor_match:
                    continue
                
                valor_str = valor_match.group(1)
                eh_saida = "-" in linha[linha.find(valor_str):linha.find(valor_str) + 20]
                
                # Extrair descrição
                descricao = re.sub(r"^\d{2}/\d{2}\s+", "", linha)
                descricao = re.sub(r"\d{1,3}(?:\.\d{3})*,\d{2}-?$", "", descricao).strip()
                descricao = limpar_historico(descricao) if descricao else "Operação Bancária"
                
                # Formatar data para YYYY-MM-DD
                from datetime import datetime
                ano_atual = datetime.now().year
                try:
                    dia, mes = data.split("/")
                    data_formatada = f"{ano_atual}-{mes}-{dia}"
                except:
                    data_formatada = data
                
                # Classificar
                conta_classificada, nome_conta, terceiro = classify_extrato(descricao)
                
                data_rows.append({
                    "Data": data_formatada,
                    "Historico": descricao,
                    "FORNECEDOR": "",
                    "NOME_CONTA": nome_conta,
                    "CONTA_CREDITO": "11204" if not eh_saida else "",
                    "CONTA_DEBITO": "11204" if eh_saida else "",
                    "TERCEIRO": terceiro,
                })
    
    return pd.DataFrame(data_rows)

def process_extrato(pdf_content):
    """Processa extrato bancário detectando automaticamente o banco"""
    
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        texto_completo = ""
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                texto_completo += texto + "\n"
    
    banco = detect_bank(texto_completo)
    
    if banco == "BB":
        return process_extrato_bb(pdf_content)
    elif banco == "SANTANDER":
        return process_extrato_santander(pdf_content)
    elif banco == "ITAU":
        return process_extrato_itau(pdf_content)
    else:
        raise Exception(f"Banco não identificado no PDF. Detectado: {banco}")