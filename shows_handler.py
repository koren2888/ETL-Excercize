import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

from config import config
from es_connector import EsConnector
from models.show import Show


class ShowsHandler:
    def __init__(self, csv_folder=config['data.folder'], csv_filename=config['data.shows_filename']):
        self.csv_path = os.path.join(csv_folder, csv_filename)
        self.shows_df = pd.read_csv(self.csv_path)
        pd.set_option('display.max_columns', None)

        self.es_connector = EsConnector(index_name="netflix_show")

        self.duration_by_director_df = None
        self.category_per_country_df = None
        self.modify_df()

        if config["elastic.init_data"]:
            self.df_to_elastic(self.shows_df)

    def modify_df(self):
        self.shows_df = self.shows_df[self.shows_df["release_year"] >= 2016]
        self.shows_df = self.shows_df.where(pd.notnull(self.shows_df), None)

        self.shows_df["current_date"] = datetime.now().date()
        self.shows_df["number_of_categories"] = self.shows_df.apply(lambda row: len(row.listed_in.split(',')) + 1,
                                                                    axis=1)
        self.shows_df["duration_in_seconds"] = self.shows_df.apply(ShowsHandler.get_duration_in_seconds, axis=1)

        self.duration_by_director_df = self.shows_df.groupby(["director"]).agg({"duration_in_seconds": ["mean"]})

        country_rows_df = self.shows_df.assign(country=self.shows_df.country.str.split(",")).explode('country')
        self.category_per_country_df = country_rows_df.groupby(["country"]).agg({"number_of_categories": ["sum"]})

    @staticmethod
    def get_duration_in_seconds(row):
        if not row["duration"]:
            return 0
        duration, duration_type = row["duration"].split(" ")
        if "min" != duration_type:
            return int(duration) * 300 * 60
        else:
            return int(duration) * 60

    def df_to_elastic(self, df):
        for row in tqdm(df.to_dict(orient="records")):
            self.es_connector.insert_doc(row)

    def add_show(self, show: Show):
        show_dictionary = show.dict()

        show_dictionary["current_date"] = datetime.now().date()
        show_dictionary["number_of_categories"] = len(show.listed_in.split(',')) + 1
        show_dictionary["duration_in_seconds"] = ShowsHandler.get_duration_in_seconds(show_dictionary)

        self.shows_df.append(show.dict(), ignore_index=True)
        self.es_connector.insert_doc(show_dictionary)

    def delete_show(self, show_id):
        self.shows_df = self.shows_df[self.shows_df.show_id != show_id]
        self.es_connector.delete_doc({"show_id": show_id})

    def df_to_graph(self):
        figure, axis = plt.subplots(2, 3, figsize=(13, 7))
        shows_types_pie = self.shows_df.type.value_counts().plot\
            .pie(autopct='%1.0f%%', ax=axis[0, 0], title='Shows Types')

        movies_duration_hist = self.shows_df[self.shows_df.type == "Movie"]\
            .apply(lambda row: row["duration_in_seconds"] / 60, axis=1)\
            .hist(bins=25, grid=False, color='#86bf91', zorder=2, rwidth=0.9, ax=axis[0, 1])
        axis[0, 1].set_title('Movies Duration')

        tv_shows_duration_hist = self.shows_df[self.shows_df.type == "TV Show"]\
            .apply(lambda row: row["duration_in_seconds"] / 300 / 60, axis=1)\
            .hist(bins=25, grid=False, color='#86bf91', zorder=2, rwidth=0.9, ax=axis[0, 2])
        axis[0, 2].set_title('TV Shows Duration')

        tv_shows_rating_bar = self.shows_df[self.shows_df.type == "TV Show"].rating.value_counts().plot\
            .bar(grid=False, color='#86bf91', zorder=2, ax=axis[1, 0], title='TV Shows Rating')

        movies_rating_bar = self.shows_df[self.shows_df.type == "Movie"].rating.value_counts().plot\
            .bar(grid=False, color='#86bf91', zorder=2, ax=axis[1, 1], title='Movies Rating')

        axis[1, 2].axis('off')

        plt.show()
