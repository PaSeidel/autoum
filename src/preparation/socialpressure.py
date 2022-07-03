import os
import sys

import pandas as pd
from dotenv import load_dotenv
from sklearn import preprocessing

load_dotenv()
root = os.getenv("ROOT_FOLDER")
sys.path.append(root + "src/")

from preparation.helper.helper_preparation import eda

pd.set_option('display.max_columns', 200)
pd.set_option('display.width', None)

class SocialPressure:

    def __init__(self):

        ## Define paths
        load_dotenv()
        self.parent_folder = os.getenv("ROOT_FOLDER")
        self.data_folder = self.parent_folder + "data/"
        self.social_pressure_path = self.data_folder + "social-pressure/"
        self.social_pressure_original_path = self.social_pressure_path + "social_pressure.csv"
        self.social_pressure_neighbors_path = self.social_pressure_path + "social_pressure_neighbors.csv"

    def prep(self):
        """
        Prepare the social pressure dataset and store the csv files in the filesystem.

        1. Apply LabelEncoder on categorical columns
        2. Create target column with a binary value
        3. Create response column(s)
        4. Remove duplicates
        """
        data = pd.read_csv(self.social_pressure_original_path)

        ## 1. Apply LabelEncoder on categorical columns
        le = preprocessing.LabelEncoder()
        data.sex = le.fit_transform(data.sex)
        data.g2000 = le.fit_transform(data.g2000)
        data.g2002 = le.fit_transform(data.g2002)
        data.g2004 = le.fit_transform(data.g2004)
        data.p2000 = le.fit_transform(data.p2000)
        data.p2002 = le.fit_transform(data.p2002)
        data.p2004 = le.fit_transform(data.p2004)

        ## 2. Create target column with a binary value
        data["response"] = [1 if x == "Yes" else 0 for x in data.voted]
        data.drop((["voted"]), axis=1, inplace=True)

        # 3. Create treatment column
        # Rename treatment in order to replace old treatment with new treatment
        data.rename(columns={
            'treatment': 'treatment_ind'
        }, inplace=True)

        data_neighbors = data.loc[data["treatment_ind"].isin([" Neighbors", " Control"])].copy()
        data_neighbors["treatment"] = [0 if x == " Control" else 1 for x in data_neighbors.treatment_ind]
        data_neighbors.drop((["treatment_ind"]), axis=1, inplace=True)

        data_no_treatment = data_neighbors.loc[data_neighbors.treatment == 0]
        data_treatment = data_neighbors.loc[data_neighbors.treatment == 1]
        frac = round(data_treatment.shape[0] / data_no_treatment.shape[0], 3)
        data_no_treatment = data_no_treatment.sample(frac=frac)
        data = pd.concat([data_no_treatment, data_treatment]).sample(frac=1)

        # 4. Remove duplicates
        data.drop_duplicates(inplace=True, ignore_index=True)
        data.reset_index(inplace=True, drop=True)

        # Save treatment data frames to file
        data.to_csv(self.social_pressure_neighbors_path, index=False)


if __name__ == '__main__':
    social_pressure = SocialPressure()
    social_pressure.prep()
    eda(social_pressure.social_pressure_neighbors_path)
