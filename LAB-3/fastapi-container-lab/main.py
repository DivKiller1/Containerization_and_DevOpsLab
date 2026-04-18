from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html>
<head><title>Container Lab</title></head>
<body>
<h1>FastAPI Container Lab</h1>
<p>Name: Divyanshu Gaur</p>
<p>SAP: 500121752</p>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse(html_content))
async def root():
    return html_content
