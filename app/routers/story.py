from fastapi import Response, status, HTTPException, Depends, APIRouter,  WebSocket, WebSocketDisconnect, Cookie, WebSocketException, Query, status, Request
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

from ..websocket import manager   # Import your WebSocket manager here
from ..utils import generate_unique_code, rooms  # Import your utility function for generating codes here
from icecream import ic
from typing import Annotated, Union



async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[Union[str, None], Cookie()] = None,
    token: Annotated[Union[str, None], Query()] = None,
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


router = APIRouter()

@router.websocket("/join/{room}")
async def join_room(websocket: WebSocket, room: str, db: Session = Depends(get_db)):

    request_header_dict = dict(websocket.headers)
    access_token = request_header_dict['access_token']
    current_user = oauth2.get_current_user(access_token)
   
    rooms.append(room)

    if room not in rooms:
        return {"error": "Room not found"}

    await manager.connect(websocket, room)
    await manager.send_personal_message(f"You# joined the room {room}", websocket)
    await manager.broadcast(f"User# {current_user.email} joined the room", websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You#: {data}", websocket)
            await manager.broadcast(f"User# {current_user.email} says: {data}", websocket, room)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(f"User# {current_user.email} left the room", websocket, room)





# Create a room
@router.websocket("/create")
async def create_room(websocket: WebSocket, db: Session = Depends(get_db)):
    request_header_dict = dict(websocket.headers)
    
    # check if access_token is in the header
    if('access_token' not in request_header_dict.keys()):
        ic("No access token")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    # else get access token
    access_token = request_header_dict['access_token']
    
    current_user = oauth2.get_current_user(access_token)


    room = generate_unique_code(10)
    rooms.append(room)
    ic(len(rooms))
    ic("Limit is 10000")
    if(len(rooms) > 10000):
        rooms.popleft()


    await manager.connect(websocket, room)
    await manager.send_personal_message(f"You# created the room {room}", websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You#: {data}", websocket)
            await manager.broadcast(f"User# {current_user.email} says: {data}", websocket, room)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(f"User# {current_user.email} left the room", websocket, room)
