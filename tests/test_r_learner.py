import unittest

import numpy as np
from sklearn.model_selection import train_test_split

from autoum.approaches.r_learner import RLearner
from autoum.approaches.utils import ApproachParameters, DataSetsHelper
from autoum.datasets.utils import get_data_home, get_hillstrom_women_visit


class TestRLearner(unittest.TestCase):

    def setUp(self):
        # Get data
        data = get_hillstrom_women_visit()
        data = data.sample(frac=0.5, random_state=123)
        df_train, df_test = train_test_split(data, test_size=0.2, shuffle=True, random_state=123)
        df_train, df_valid = train_test_split(df_train, test_size=0.2, shuffle=True, random_state=123)

        self.df_train = df_train
        self.df_valid = df_valid
        self.df_test = df_test

        ds_helper = DataSetsHelper(df_train=df_train, df_valid=df_valid, df_test=df_test)
        root = f"{get_data_home()}/testing/models/"
        approach_params = ApproachParameters(cost_sensitive=False, feature_importance=False, path=root, post_prune=False, save=False, split_number=0)
        self.ds_helper = ds_helper
        self.approach_params = approach_params

        self.r_learner_parameters = {
            'n_estimators': 5,
            'max_depth': 5,
            'max_features': 5,
            'random_state': 123,
            "n_jobs": 10
        }

    def test_analyze(self):
        r_learner = RLearner(self.r_learner_parameters, self.approach_params)
        dict_scores = r_learner.analyze(self.ds_helper)

        self.check_scores(dict_scores["score_train"], self.df_train, r_learner=True)
        self.check_scores(dict_scores["score_valid"], self.df_valid, r_learner=True)
        self.check_scores(dict_scores["score_test"], self.df_test, r_learner=True)

    def check_scores(self, scores, df, min=-1, r_learner=False):
        # Check if the number of scores is equal to the number of rows
        self.assertEqual(len(scores), df.shape[0])
        # Check if scores is an nd.array
        self.assertIsInstance(scores, np.ndarray)  # Check if the scores are all >= -1
