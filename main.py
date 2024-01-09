# server
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import fastapi.middleware.cors as CORS

# my modules
from ai import Gemini
from db import ChatDB

# models
from models import TokenData, User, ChatHistory, Token

# authentication
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from authentication import Auth


app = FastAPI()
app.add_middleware(
    CORS.CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


gemini = Gemini()
chat_db = ChatDB()
auth = Auth()

async def get_current_user(token: str = Depends(auth.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    user = auth.get_user(chat_db, token_data.user_id)

    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(chat_db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user_id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/chat")
async def chat(chat_history: ChatHistory, current_user=Depends(get_current_user)):
    try:
        message = chat_history.model_dump()["content"]
        response = gemini.chat(message)

        def generate():
            for part in response:
                yield from part.text

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@app.get("/user/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/register")
async def register(user_id: str, password: str):
    hashed_password = auth.get_password_hash(password)

    try:
        chat_db.create_user(user_id, hashed_password)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()
    port = args.p

    uvicorn.run(app, host="0.0.0.0", port=port)
