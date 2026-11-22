from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
import functions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#A1
@app.post("/register")
def register(username: str = Body(), email: str = Body(), password: str = Body()):
    return function. register(username=username, email=email, password=password)


#A2 
@app.post("/login" )
def login(email: str = Body(), password: str = Body()):
    return function. login(email=email, password=password)


#A3
@app.post("/refresh")
def refresh(refresh_token: str = Body(None, embed=True), token=Header(None)):
    token_to_use = refresh_token or token
    if not token_to_use:
        raise HTTPException(status_code=401, detail="Refresh token required")
    return function. refresh(token_to_use)


#E1
@app.get("/get_notes")
def get_notes(token=Header(None), authorization=Header(None)):
    user = functions.get_current_user(authorization=authorization, token=token)
    return function. get_notes(user_id=user["user_id"])


#E2
@app.post("/create_note")
def create_note(
    title: str = Body(),
    content: str = Body(),
    token=Header(None),
    authorization=Header(None),
):
    user = functions.get_current_user(authorization=authorization, token=token)
    return function.create_note(user_id=user["user_id"], title=title, content=content)