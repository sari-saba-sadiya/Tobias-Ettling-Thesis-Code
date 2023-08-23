import os

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import MinMaxScaler

import config
from helper import load_object, equalize_classes
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from skopt import BayesSearchCV


os.chdir('../')

training_sets = ['TS2/']
set_vary = ['meanEpochs/', 'meanEpochs/onlyEC/', 'meanEpochs/onlyEO/']
for ts in training_sets:
    for sv in set_vary:
        set_path = config.SET_PATH + ts + sv
        data = load_object(set_path + 'training_set')
        x = data['x']
        groups = data['group']
        y = data['y']

        y_skf = [int(age*10) for age in data['y']]
        y_skf = equalize_classes(y_skf)
        skf_vals = []
        skf = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=126)
        for fold, (train_index, test_index) in enumerate(skf.split(x, y, groups)):
            skf_vals.append((train_index, test_index))

        scaler = MinMaxScaler()
        x = scaler.fit_transform(x)

        parameter_space = {
            'max_depth': [45, 100],
            'min_samples_split': [2, 10],
            'min_samples_leaf': [2, 9],
            'min_weight_fraction_leaf': [0, 0.5],
            'min_impurity_decrease': [0, 0.9],
        }

        model = RandomForestRegressor(n_estimators=4000, n_jobs=30)

        fit_param = {
            'early_stopping_rounds': 200,
        }

        clf = BayesSearchCV(estimator=model,
                            search_spaces=parameter_space,
                            fit_params=fit_param,
                            cv=skf_vals,
                            scoring='neg_mean_absolute_error',
                            verbose=4)

        clf.fit(x, y=y)

        print(clf.cv_results_)
        print(clf.best_score_)
        print(clf.best_params_)
        results = pd.DataFrame(clf.cv_results_)
        results.to_csv(config.BASE_PATH + 'RandomForrest/results.csv')
