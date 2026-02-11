from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import pandas as pd
import traceback
from engine import process_pagamentos, process_recebimentos
from extrato_engine import process_extrato

app = FastAPI(title="API de Conciliação Bancária")

# Configurar CORS para permitir que o frontend acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/processar")
async def processar_pdf(
    file: UploadFile = File(...),
    tipo: str = Form(...)
):
    try:
        content = await file.read()
        
        if tipo == "PAGAMENTO":
            df = process_pagamentos(content, {})
        elif tipo == "RECEBIMENTO":
            df = process_recebimentos(content)
        elif tipo == "EXTRATO":
            df = process_extrato(content)
        else:
            return {"error": "Tipo inválido. Use PAGAMENTO, RECEBIMENTO ou EXTRATO"}
        
        if df.empty:
            return {"error": "Nenhum dado foi extraído do PDF. Verifique o formato do arquivo."}
        
        # Criar Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Conciliação')
        output.seek(0)
        
        filename = f"conciliacao_{tipo.lower()}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return {"error": f"Erro ao processar: {str(e)}"}

@app.get("/")
def health_check():
    return {"status": "online", "message": "Motor de Conciliação Ativo", "tipos_suportados": ["PAGAMENTO", "RECEBIMENTO", "EXTRATO"]}

@app.options("/processar")
async def options_processar():
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)