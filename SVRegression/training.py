import sys

sys.path.insert(0, '/home/modelrep/sadiya/tobias_ettling/ML_Models_BrainAge')

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.svm import SVR
from skopt import BayesSearchCV

from config import SET_PATH, BASE_PATH
from helper import load_object

pid = int(sys.argv[1])

training_sets = ['TS2/', 'TS4/']
set_vary = ['meanEpochs/', 'meanEpochs/onlyEC/', 'meanEpochs/onlyEO/']
for ts in training_sets:
    sv = set_vary[pid]
    set_path = SET_PATH + ts + sv
    data = load_object(set_path + 'training_set')
    x = data['x']
    groups = data['group']
    y = data['y']

    y_skf = [int(age) for age in data['y']]
    skf_vals = []
    skf = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=126)
    for fold, (train_index, test_index) in enumerate(skf.split(x, y_skf, groups)):
        skf_vals.append((train_index, test_index))

    scaler = StandardScaler()
    x = scaler.fit_transform(x)

    parameter_space = {
        'degree': np.arange(2, 6),
        'C': np.linspace(1, 20, 15),
        'epsilon': np.linspace(0.001, 5, 10),
        'gamma': np.linspace(0.001, 5, 15),
        'kernel': ['poly', 'rbf']
    }

    model = SVR(max_iter=4000)

    clf = BayesSearchCV(estimator=model,
                        search_spaces=parameter_space,
                        cv=skf_vals,
                        n_jobs=30,
                        scoring='neg_mean_absolute_error',
                        verbose=4)

    clf.fit(x, y=y)

    print(clf.cv_results_)
    print(clf.best_score_)
    print(clf.best_params_)
    results = pd.DataFrame(clf.cv_results_)
    f_name = ts.replace('/', '_') + sv.replace('/', '_')
    results.to_csv(BASE_PATH + f'SVRegression/{f_name}results.csv')
