from typing import Optional

from pydantic import BaseModel


class Show(BaseModel):
    show_id: str
    type: Optional[str]
    title: Optional[str]
    director: Optional[str]
    cast: Optional[str]
    country: Optional[str]
    date_added: Optional[str]
    release_year: Optional[str]
    rating: Optional[str]
    duration: Optional[str]
    listed_in: Optional[str]
    description: Optional[str]
