import uvicorn

if __name__ == "__main__":
    print("Launching AI Interview Intelligence System Server on http://localhost:8000")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
