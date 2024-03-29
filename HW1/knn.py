import logging
import math
import pandas

import numpy as np
import pandas as pd

class KNN:
    def __init__(self, classes, train_df, k, distance = None, normalize_data = False, verbose = False):
        logging.debug('Creating KNN...')
        self.normalize_data = normalize_data
        self.means_col = None
        self.std_devs_col = None
        self.verbose = verbose
        self.training_data = {"points": train_df, "normalized_points": self._get_normalized_data(train_df) if normalize_data else train_df, "classes": classes}
        self.k = k
        self.distance = lambda a,b : np.linalg.norm(a-b, ord = 2)
        if self.distance is not None:
            self.distance = distance
        # self.cache = []

    def classify(self, orig_point, leave_one_out = False):
        point = orig_point
        if self.normalize_data:
            point = self._get_normalized_data(orig_point)
        if self.verbose:
            print("Classifying: (%d,%d)" %(int(orig_point[0]), int(orig_point[1])))
            print("Normalized point: (%f,%f)" %(float(point[0]), float(point[1])))
        dist_idx_pairs = [[None,idx] for idx in xrange(0,len(self.training_data["normalized_points"]))]
        distances = self.training_data["normalized_points"].apply(lambda training_point: self.distance(training_point, point), axis = 1)
        # print(distances)
        # TODO: directly use pandas for selection and stuff too
        #for idx, row in enumerate(self.training_data["points"].values):
        for idx in range(0, len(distances)):
            dist = distances.iloc[idx] #self.distance(row, point)
            # print(self.distance(self.training_data["points"].values[idx], point) - dist)
            dist_idx_pairs[idx][0] = dist
        dist_idx_pairs.sort(key = lambda pair: pair[0])

        counts = {}
        total_count = 0
        if self.verbose:
            print("Nearest five points:")
            for dist,idx in dist_idx_pairs[:5]:
                close_point = self.training_data["points"].iloc[idx]
                print("Point: (%02d,%02d) | Distance: %9f | Class: %d" % ( int(close_point[0]), int(close_point[1]), float(dist), self.training_data["classes"][idx] ) )
        for idx in range(0, len(dist_idx_pairs)):
            dist, idx_actual = dist_idx_pairs[idx]
            cat = self.training_data["classes"][idx_actual]
            if leave_one_out and dist == 0.0:
                continue
            total_count += 1
            if cat not in counts:
                counts[cat] = 0
            counts[cat] += 1
            if total_count == self.k:
                break
        max_count = max(counts.values())
        cat = [k for (k,v) in counts.items() if v is max_count]
        if len(cat) > 1:
            if self.verbose:
                print("Tie, resolving with nearer first point")
            for i in range(0, self.k):
                min_cat = self.training_data["classes"][dist_idx_pairs[i][1]]
                if min_cat in cat:
                    return min_cat
        return max(counts, key=lambda x: counts[x])

    def _find_means_and_stddev(self, df):
        self.means_col = df.mean(0)
        self.std_devs_col = df.std(0)
        return

    def _get_normalized_data(self, df):
        if self.means_col is None or self.std_devs_col is None:
            self._find_means_and_stddev(df)
        if type(df) is not pandas.core.frame.DataFrame:
            df_new = []
            for i in range(0,len(df)):
                df_new.append((df[i]-self.means_col[i])/self.std_devs_col[i])
        else:
            return (df - df.mean()) / (df.std())
            """
            df_new = df.copy()
            for i in range(0, len(df.iloc[0])):
                df_new.iloc[:, i] = df.iloc[:, i].apply(lambda x: (x-self.means_col[i])/self.std_devs_col[i])
            """
        return df_new
