from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import pandas as pd
from engine import process_pagamentos, process_recebimentos
from extrato_engine import process_extrato

app = FastAPI(title="API de Conciliação Bancária")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois pode restringir
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
            raise HTTPException(
                status_code=400,
                detail="Tipo inválido. Use PAGAMENTO, RECEBIMENTO ou EXTRATO"
            )

        if df.empty:
            raise HTTPException(
                status_code=422,
                detail="Nenhum dado foi extraído do PDF."
            )

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Conciliação")
        output.seek(0)

        filename = f"conciliacao_{tipo.lower()}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar o arquivo: {str(e)}"
        )

@app.get("/")
def health_check():
    return {
        "status": "online",
        "message": "Motor de Conciliação Ativo",
        "tipos_suportados": ["PAGAMENTO", "RECEBIMENTO", "EXTRATO"],
    }
