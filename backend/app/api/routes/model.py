from fastapi import APIRouter

router = APIRouter()


@router.get("/current")
async def current_model():
    return {"version_tag": None, "is_active": False, "status": "no_active_model"}


@router.post("/reload")
async def reload_model():
    return {"status": "accepted", "message": "Model reload is not configured"}