# sacco_core/api/goaml_api.py
# Optional: a tiny FastAPI to accept STR/CTR XML and record submission.
# Run separately: `uvicorn sacco_core.api.goaml_api:app --reload --port 8081`
from __future__ import annotations
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from sacco_core.aml.submissions import save_submission

app = FastAPI(title="goAML Lightweight Receiver")

@app.post("/submit")
async def submit(kind: str = Form(...), key_ref: str = Form(...), file: UploadFile = Form(...)):
    try:
        xml_bytes = await file.read()
        xml_text = xml_bytes.decode("utf-8", errors="ignore")
        sid = save_submission(kind=kind, key_ref=key_ref, xml_text=xml_text, status="Submitted")
        return JSONResponse({"ok": True, "submission_id": sid})
    except Exception as e:
        sid = save_submission(kind=kind, key_ref=key_ref, xml_text="", status="Error", error_message=str(e))
        return JSONResponse({"ok": False, "submission_id": sid, "error": str(e)}, status_code=500)