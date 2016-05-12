import numpy as np

from databaseconnector import DatabaseConnector
from collections import Counter

class LVQ():
    def __init__(self, database_name):
        self.db = DatabaseConnector(database_name)

    def init_ref_vector(self):
        '''
        0 = id
        1 = file_id
        2 = frame
        3 = feature
        4 = class
        '''
        return np.asarray(self.db.select_random("features","class"), dtype=object)

    def init_data_set(self, ref_vector):
        '''
        0 = id
        1 = file_id
        2 = frame
        3 = feature
        4 = class
        '''
        return np.asarray(self.db.select_exclude("features","id",ref_vector[:,0]), dtype=object)

    def eucl(self, x, y):
        return np.sqrt(np.sum((x - y) ** 2))

    def start_training(self,ref_vectors, data_set, max_epoh, alpha, alpha_decay):
        old_weight = ref_vectors[:,3]
        # new_weight = np.zeros((len(ref_vectors),ref_vectors[0,3].shape[0]))
        new_weight = ref_vectors[:,[3,4]]

        while max_epoh > 0 and alpha > 0.01:
            for data in data_set:
                temp = []
                for ref in ref_vectors:
                    # temp.append([ref[4],self.eucl(data[3],ref[3])])
                    temp.append(self.eucl(data[3], ref[3]))

                # print "temp : "+str(temp)
                # print "dataset : "+str(data)+"\nindex: "+str(index)
                # print "panjang temp: "+str(len(temp))
                index = np.argmin(temp)
                data_min = ref_vectors[index]

                if(str(data_min[4]) == str(data[4])):
                    new_weight[index,0] = old_weight[index] - alpha * (data[3] - old_weight[index])
                else:
                    new_weight[index,0] = old_weight[index] + alpha * (data[3] - old_weight[index])

            max_epoh-=1
            alpha-=(alpha_decay * alpha)

        return new_weight

    def test_data(self, features):

        self.final_weight = np.asarray(self.db.select("final_weight"), dtype=object)

        candidate = []
        for feat in features:
            temp = []
            for weight in self.final_weight:
                temp.append(self.eucl(feat, weight[0]))

            index = np.argmin(temp)
            candidate.append(str(self.final_weight[index,1]))

        c = Counter(candidate)

        return c.most_common()


