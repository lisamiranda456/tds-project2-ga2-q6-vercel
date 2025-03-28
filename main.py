import os
import json
import base64
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GITHUB_URL = "https://api.github.com/repos/danielrayappa2210/TDS-Project-2---datastore/contents/q-vercel-python.json"

app = FastAPI()

@app.get("/api")
async def api(name: list[str] = Query(...)):
    headers = {}
    if ACCESS_TOKEN:
        headers["Authorization"] = f"token {ACCESS_TOKEN}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(GITHUB_URL, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching JSON from GitHub")
    content = resp.json().get("content")
    if not content:
        raise HTTPException(status_code=500, detail="No content found in GitHub response")
    try:
        decoded = base64.b64decode(content)
        students_data = json.loads(decoded)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    marks = []
    for student_name in name:
        found = False
        for student in students_data:
            if student.get("name") == student_name:
                marks.append(student.get("marks"))
                found = True
                break
        if not found:
            marks.append("Name not found")
    
    response = JSONResponse(content={"marks": marks})
    response.headers.update({
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })
    return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
