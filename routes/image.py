from sqlmodel import Session, select
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

# internal imports
from models import db, ImageMetadata
from processors import ImageProcessor

router = APIRouter()


@router.get("", response_model=list[ImageMetadata])
async def get_images(session: Session = Depends(db.get_session)):
    query = select(ImageMetadata)
    return session.exec(query).all()


@router.get("/{id}", response_model=ImageMetadata)
async def get_image(id: int, session: Session = Depends(db.get_session)):
    result = session.get(ImageMetadata, id)

    if result:
        return result

    raise HTTPException(status_code=404, detail=f"ID {id} does not exist")


@router.post("/upload", response_model=ImageMetadata)
async def upload_image(
    file: UploadFile = File(...),
    session: Session = Depends(db.get_session),
):
    extension = file.filename.split(".")[-1]
    if extension.lower() != "tiff":
        raise HTTPException(status_code=400, detail="Only TIFF file is allowed")

    media_path = await ImageProcessor.save_image(file)
    image = ImageMetadata(media_path=media_path)
    image.save(session)

    return image


@router.get("/{id}/statistics")
async def get_stats(id: int, session: Session = Depends(db.get_session)):
    image = session.get(ImageMetadata, id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail=f"Image does not exists with id {id}",
        )
    processor = ImageProcessor(image=image)
    return processor.stats()
