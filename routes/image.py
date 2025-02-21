from fastapi import APIRouter

router = APIRouter()


@router.post("upload")
async def read_users():
    return {"success": True}
