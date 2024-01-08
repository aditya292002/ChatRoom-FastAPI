from fastapi import Response, status, HTTPException, Depends, APIRouter,  WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

from ..websocket import manager   # Import your WebSocket manager here
from ..utils import generate_unique_code, rooms  # Import your utility function for generating codes here


router = APIRouter()


# @app.websocket("/ws/{client_id}")  -- exmaple
router = APIRouter()


@router.websocket("/join/{room}")
async def join_room(websocket: WebSocket, room: str, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):

# ------------------- testing ------------------------------------------------------------------
# async def join_room(websocket: WebSocket, room: str, db: Session = Depends(get_db)):
    
#     current_user = db.query(models.User).filter(    
#         models.User.email == "adikeshari292002@gmail.com").first()
# -------------------------- End testing -------------------------------------------------------    

    if room not in rooms:
        return {"error": "Room not found"}

    await manager.connect(websocket, room)
    await manager.broadcast(f"User# {current_user.email} joined the room", websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"User# {current_user.email}: {data}", websocket)
            await manager.broadcast(f"User# {current_user.email} says: {data}", websocket, room)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"User# {current_user.email} left the room")


@router.websocket("/create")
async def create_room(websocket: WebSocket, db: Session = Depends(get_db),
                      current_user: int = Depends(oauth2.get_current_user)):
# ------------------- testing ------------------------------------------------------------------

# async def create_room(websocket: WebSocket, db: Session = Depends(get_db)):
#     current_user = db.query(models.User).filter(    
#         models.User.email == "newaditya12002@gmail.com").first()
#     print("entered without sec")
# -------------------------- End testing -------------------------------------------------------    

    room = generate_unique_code(10)
    rooms.append(room)

    await manager.connect(websocket, room)
    await manager.send_personal_message(f"User {current_user.email} created the room {room}", websocket)
    # await manager.broadcast(f"User {current_user.email} joined the room", websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"User# {current_user.email}: {data}", websocket)
            await manager.broadcast(f"User# {current_user.email} says: {data}", websocket, room)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"User# {current_user.email} left the room")
