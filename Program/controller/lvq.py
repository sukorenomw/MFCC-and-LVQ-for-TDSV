import numpy as np
from databaseconnector import DatabaseConnector

class LVQ():
    def __init__(self):
        self.db = DatabaseConnector()

    def init_ref_vector(self):
        self.ref_vector = []
        data = self.db.select_group("output_classes","class")