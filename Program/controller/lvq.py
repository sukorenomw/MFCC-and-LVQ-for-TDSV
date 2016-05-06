import numpy as np
from databaseconnector import DatabaseConnector

class LVQ():
    def __init__(self):
        self.db = DatabaseConnector()

    def init_ref_vector(self):
        return self.db.select_group("features","class")

    def init_data_set(self):
        not_in = []
        for data in self.ref_vector:
            not_in.append(data['id'])

        return self.db.select_exclude("features","id", not_in)

    def eucl(self,x, y):
        return np.sqrt(np.sum((x - y) ** 2))

    def start_training(self,ref_vector, data_set):


