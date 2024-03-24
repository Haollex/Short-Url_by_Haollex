import secrets
from pydantic import BaseModel
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import RedirectResponse

from database import Database

app = FastAPI

class URLItem(BaseModel):
    url: str

@app.post("/create/")
def create_short_url(url_item: URLItem):
    short_url = secrets.token_urlsafe(6)
    db = Database()
    url = db.save_url(short_url, url_item.url)
    if url:
        return {"short_url": f"http://shorter-urls.com/{url}"}
    return {"short_url": f"http://shorter-urls.com/{short_url}"}

@app.get("/(short_url)")
def redirect(short_url: str = Query(None, description="Redirect short url")):
    db = Database()
    original_url = db.get_original_url(short_url)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    country = Request.headers.get("X-Forwarded-For", "").split(",")[-1].strip()
    ip_address = Request.client.host
    visit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.save_visit(short_url, country, ip_address, visit_time)
    return RedirectResponse(url=original_url)

@app.get("/stats/")
def get_stats(short_url: str = Query(None, description="Short link for stats")):
    if short_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    db = Database()
    visit_count = db.get_stats(short_url)
    if visit_count is None:
        raise HTTPException(status_code=404, detail="Stats not found")
    return {"short_url": short_url, "visit_count": visit_count}
