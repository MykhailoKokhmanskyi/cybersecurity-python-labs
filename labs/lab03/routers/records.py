import sqlite3

from fastapi import APIRouter, HTTPException, Query, status

from labs.lab03 import repository
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=list[RecordRead])
def list_records(
    category_id: int | None = Query(None, gt=0),
    status_filter: str | None = Query(
        None, alias="status", regex="^(new|in_progress|done)$"
    ),
    min_value: float | None = Query(None, ge=0, le=100),
    q: str | None = Query(None, min_length=1, max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    if category_id is not None:
        cat = repository.get_category_by_id(category_id)
        if not cat:
            return []

    return repository.get_records(
        category_id=category_id,
        status=status_filter,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int):
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid record ID.",
        )

    rec = repository.get_record_by_id(record_id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found."
        )
    return rec


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(record: RecordCreate):
    cat = repository.get_category_by_id(record.category_id)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found."
        )

    try:
        return repository.create_record(record.model_dump())
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record with this code already exists.",
        )


@router.put("/{record_id}", response_model=RecordRead)
def replace_record(record_id: int, record: RecordReplace):
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid record ID.",
        )

    existing = repository.get_record_by_id(record_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found."
        )

    cat = repository.get_category_by_id(record.category_id)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found."
        )

    try:
        updated = repository.update_record(record_id, record.model_dump())
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Record not found."
            )
        return updated
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record with this code already exists or constraint violation.",
        )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_record(record_id: int):
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid record ID.",
        )

    success = repository.delete_record(record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found."
        )


@router.post(
    "/bulk", response_model=list[RecordRead], status_code=status.HTTP_201_CREATED
)
def create_records_bulk(records: list[RecordCreate]):
    if not records or len(records) > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Batch size must be between 1 and 100 items.",
        )

    category_ids = {r.category_id for r in records}
    for cat_id in category_ids:
        if not repository.get_category_by_id(cat_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {cat_id} not found.",
            )

    codes = [r.code for r in records]
    if len(codes) != len(set(codes)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate codes found within the batch.",
        )

    try:
        records_dict = [r.model_dump() for r in records]
        return repository.create_records_bulk(records_dict)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Integrity error (e.g. duplicate code already exists in database).",
        )
