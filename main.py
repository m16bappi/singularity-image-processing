from fastapi import FastAPI

from routes import ImageRoute

app = FastAPI()


@app.get("/")
def read_root():
    return {"healthy": True}


app.include_router(
    ImageRoute,
    prefix="/image",
    tags=["image"],
)
