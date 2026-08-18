from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import json

app = FastAPI()

DATABASE_FILE = "database.json"


def load_database():
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)


def save_database(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)


class MenuItem(BaseModel):
    name: str
    category: str
    price: float
    available: bool


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None



security = HTTPBasic()

AUTH_USERNAME = "admin"
AUTH_PASSWORD = "admin123"


def check_basic_auth(
    credentials: HTTPBasicCredentials = Depends(security)
):
    if (
        credentials.username != AUTH_USERNAME
        or credentials.password != AUTH_PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    return True



@app.get("/api/menu-items")
def get_menu_items(
    auth: bool = Depends(check_basic_auth)
):
    db = load_database()

    menu_items = db["menu_items"]

    return {
        "success": True,
        "data": menu_items
    }


@app.get("/api/menu-items/{menu_id}")
def get_menu_item(
    menu_id: int,
    auth: bool = Depends(check_basic_auth)
):
    db = load_database()

    for item in db["menu_items"]:
        if item["id"] == menu_id:
            return {
                "success": True,
                "data": item
            }

    raise HTTPException(
        status_code=404,
        detail="Menu item not found"
    )


@app.post("/api/menu-items", status_code=201)
def create_menu_item(
    menu_item: MenuItem,
    auth: bool = Depends(check_basic_auth)
):
    db = load_database()

    menu_items = db["menu_items"]

    new_id = max(
        (item["id"] for item in menu_items),
        default=0
    ) + 1

    new_menu_item = {
        "id": new_id,
        **menu_item.model_dump()
    }

    menu_items.append(new_menu_item)

    save_database(db)

    return {
        "success": True,
        "message": "Menu item created successfully",
        "data": new_menu_item
    }

@app.put("/api/menu-items/{menu_id}")
def update_menu_item(
    menu_id: int,
    menu_item: MenuItem,
    auth: bool = Depends(check_basic_auth)
):
    db = load_database()

    for item in db["menu_items"]:
        if item["id"] == menu_id:

            item.update(
                menu_item.model_dump()
            )

            save_database(db)

            return {
                "success": True,
                "message": "Menu item updated successfully",
                "data": item
            }

    raise HTTPException(
        status_code=404,
        detail="Menu item not found"
    )


@app.patch("/api/menu-items/{menu_id}")
def patch_menu_item(
    menu_id: int,
    menu_item: MenuItemUpdate,
    auth: bool = Depends(check_basic_auth)
):
    db = load_database()

    for item in db["menu_items"]:
        if item["id"] == menu_id:

            update_data = menu_item.model_dump(
                exclude_unset=True
            )

            item.update(update_data)

            save_database(db)

            return {
                "success": True,
                "message": "Menu item patched successfully",
                "data": item
            }

    raise HTTPException(
        status_code=404,
        detail="Menu item not found"
    )


@app.delete("/api/menu-items/{menu_id}")
def delete_menu_item(
    menu_id: int,
    auth: bool = Depends(check_basic_auth)
):
    db = load_database()

    menu_items = db["menu_items"]

    for item in menu_items:
        if item["id"] == menu_id:

            menu_items.remove(item)

            save_database(db)

            return {
                "success": True,
                "message": "Menu item deleted successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Menu item not found"
    )

@app.get("/api/basic-protected")
def basic_protected(
    auth: bool = Depends(check_basic_auth)
):
    return {
        "success": True,
        "msg": "welcome admin"
    }
