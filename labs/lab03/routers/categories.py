import sqlite3

from fastapi import APIRouter, HTTPException, status

from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories():
    return repository.get_categories()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate):
    try:
        return repository.create_category(category.name)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists.",
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_category(category_id: int):
    if category_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid ID."
        )

    cat = repository.get_category_by_id(category_id)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found."
        )

    try:
        success = repository.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found."
            )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category containing records (restricted foreign key).",
        )
