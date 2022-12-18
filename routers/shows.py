from fastapi import APIRouter

from models.show import Show
from shows_handler import ShowsHandler

router = APIRouter(prefix='/shows')

shows_handler = ShowsHandler()
shows_handler.df_to_graph()


@router.post(path='')
def add_show(show: Show):
    shows_handler.add_show(show)


@router.delete(path='/{show_id}')
def delete_show(show_id: str):
    shows_handler.delete_show(show_id)

