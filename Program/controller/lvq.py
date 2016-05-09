import numpy as np
from databaseconnector import DatabaseConnector

class LVQ():
    def __init__(self):
        self.db = DatabaseConnector()

    def init_ref_vector(self):
        '''
        0 = id
        1 = file_id
        2 = frame
        3 = feature
        4 = class
        '''
        return np.asarray(self.db.select_group("features","class"), dtype=object)

    def init_data_set(self, ref_vector):
        '''
        0 = id
        1 = file_id
        2 = frame
        3 = feature
        4 = class
        '''
        return np.asarray(self.db.select_exclude("features","id",ref_vector[:,0]), dtype=object)

    def eucl(self,x, y):
        return np.sqrt(np.sum((x - y) ** 2))

    def start_training(self,ref_vectors, data_set, max_epoh, alpha, alpha_decay):
        old_weight = ref_vectors[:,3]
        # new_weight = np.zeros((len(ref_vectors),ref_vectors[0,3].shape[0]))
        new_weight = ref_vectors[:,[3,4]]
        for epoh in xrange(max_epoh):
            for data in data_set:
                temp = []
                for ref in ref_vectors:
                    # temp.append([ref[4],self.eucl(data[3],ref[3])])
                    temp.append(self.eucl(data[3], ref[3]))

                # print "temp : "+str(temp)
                index = np.argmin(temp)
                # print "dataset : "+str(data)+"\nindex: "+str(index)
                # print "panjang temp: "+str(len(temp))
                data_min = ref_vectors[index]

                if(str(data_min[4]) == str(data[4])):
                    new_weight[index,0] = old_weight[index] - alpha * (data[3] - old_weight[index])
                else:
                    new_weight[index,0] = old_weight[index] + alpha * (data[3] - old_weight[index])

            alpha-=alpha_decay

        return new_weight

