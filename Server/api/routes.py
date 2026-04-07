"""
API маршруты для интеграции с лоадером
"""

from aiohttp import web
from database.db import SessionLocal
from utils.auth import login_user, register_user
from database.models import User
from datetime import datetime
import json


async def api_login(request: web.Request) -> web.Response:
    """
    POST /api/login
    Body: {"username": "...", "password": "..."}
    """
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return web.json_response(
                {"success": False, "error": "Username и пароль обязательны"},
                status=400
            )
        
        db = SessionLocal()
        try:
            success, user, msg = login_user(db, username, password)
            
            if success:
                sub_end = user.subscription_end.isoformat() if user.subscription_end else None
                
                return web.json_response({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "telegram_id": user.telegram_id,
                        "username": user.username,
                        "email": user.email,
                        "pc_type": user.pc_type,
                        "subscription_end": sub_end,
                    }
                })
            else:
                return web.json_response(
                    {"success": False, "error": msg},
                    status=401
                )
        finally:
            db.close()
    
    except Exception as e:
        return web.json_response(
            {"success": False, "error": str(e)},
            status=500
        )


async def api_register(request: web.Request) -> web.Response:
    """
    POST /api/register
    Body: {"email": "...", "username": "...", "password": "..."}
    """
    try:
        data = await request.json()
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        
        if not all([email, username, password]):
            return web.json_response(
                {"success": False, "error": "Email, username и пароль обязательны"},
                status=400
            )
        
        db = SessionLocal()
        try:
            success, msg = register_user(db, 0, email, username, password)
            
            if success:
                return web.json_response(
                    {"success": True, "message": msg},
                    status=201
                )
            else:
                return web.json_response(
                    {"success": False, "error": msg},
                    status=400
                )
        finally:
            db.close()
    
    except Exception as e:
        return web.json_response(
            {"success": False, "error": str(e)},
            status=500
        )


async def api_user_info(request: web.Request) -> web.Response:
    """
    GET /api/user/{user_id}
    """
    try:
        user_id = int(request.match_info.get("user_id"))
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return web.json_response(
                    {"success": False, "error": "Пользователь не найден"},
                    status=404
                )
            
            sub_end = user.subscription_end.isoformat() if user.subscription_end else None
            
            return web.json_response({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "pc_type": user.pc_type,
                    "subscription_end": sub_end,
                }
            })
        finally:
            db.close()
    
    except Exception as e:
        return web.json_response(
            {"success": False, "error": str(e)},
            status=500
        )


def setup_api_routes(app: web.Application):
    """Регистрирует API маршруты"""
    app.router.add_post('/api/login', api_login)
    app.router.add_post('/api/register', api_register)
    app.router.add_get('/api/user/{user_id}', api_user_info)
