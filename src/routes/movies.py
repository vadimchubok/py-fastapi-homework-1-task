from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import math

from database import get_db
from models.movies import MovieModel
from schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter()


@router.get("/movies", response_model=MovieListResponseSchema)
async def get_movies(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1),
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit

    count_query = select(func.count()).select_from(MovieModel)
    count_result = await db.execute(count_query)
    total_items = count_result.scalar()

    total_pages = math.ceil(total_items / limit) if total_items > 0 else 1

    movie_query = select(MovieModel).offset(offset).limit(limit)
    movie_result = await db.execute(movie_query)
    movies = movie_result.scalars().all()

    prev_page = f"/movies?page={page - 1}&limit={limit}" if page > 1 else None
    next_page = f"/movies?page={page + 1}&limit={limit}" if page < total_pages else None

    return {
        "movies": movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_items
    }


@router.get("/movies/{movie_id}", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    query = select(MovieModel).where(MovieModel.id == movie_id)
    result = await db.execute(query)
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie
