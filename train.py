# -*- coding: utf-8 -*-
"""
Created on Sun May  9 17:45:48 2021

@author: ZZ03MG668
"""

import numpy as np
import pandas as pd

df = pd.read_csv('processed_dataset.csv', index_col = 0)

df_to_split = df.copy()

df_1 = ('small', df_to_split[df_to_split['rooms'] == 1])
df_2 = ('medium', df_to_split[df_to_split['rooms'] == 2])
df_3 = ('large', df_to_split[(df_to_split['rooms'].eq(3) | df_to_split['rooms'].eq(4))])

print(f'1: {df_1[1].shape[0]}, 2: {df_2[1].shape[0]}, 3: {df_3[1].shape[0]}')

model_dict = {}

for idx, dataset in [df_1, df_2, df_3]:    
    
    import warnings
    warnings.simplefilter('ignore')
    
    # SPLIT
    
    from sklearn.model_selection import train_test_split
    
    dataset['price_quantiles'] = pd.qcut(dataset['price'], q = 5)
    y = dataset.pop('price').astype(float)
    X = dataset

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify = dataset['price_quantiles'])
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42, stratify = X_train['price_quantiles'])

    for i in [X_train, X_val, X_test]:
        del i['price_quantiles']
    
    X_train = np.array(X_train)
    X_test = np.array(X_test)
    X_val = np.array(X_val)
    
    # TRAIN
    
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, BaggingRegressor
    from lightgbm import LGBMRegressor
    from xgboost import XGBRegressor
    from sklearn.model_selection import KFold, cross_val_score

    # set up kfold CV
    kfold = KFold(n_splits = 5, random_state = 42, shuffle = True)

    # instantiate estimators 
    lgbm = LGBMRegressor(objective = 'regression',
                         random_state = 42,
                         learning_rate = 0.1,
                         max_depth = 12,
                         reg_alpha = 0.2,
                         reg_lambda = 0.2,
                         subsample = 0.4,
                         min_child_weight = 0.001,
                         n_estimators = 200).fit(X_train, y_train)
    xgbr = XGBRegressor(objective = 'reg:squarederror',
                         eta = 0.1,
                         max_depth = 7,
                         reg_alpha = 0.2,
                         reg_lambda = 0.2,
                         subsample = 0.7,
                         colsample_bylevel = 0.75,
                         colsample_bytree = 0.75).fit(X_train, y_train)
    bagging = BaggingRegressor(random_state = 42, n_estimators = 200)
    forest = RandomForestRegressor(random_state = 42, n_estimators = 200)
    gboost = GradientBoostingRegressor(random_state = 42, n_estimators = 200)

    # set list of estimators
    estimators = [forest, gboost, bagging, xgbr, lgbm]
    
    from sklearn.metrics import r2_score
    from sklearn.metrics import mean_squared_error

    models = {}

    for estimator in estimators:

        estimator_name = estimator.__class__.__name__
        
        model = estimator.fit(X_train, y_train)

        models[estimator_name] = model

        RMSE = round(np.sqrt(-cross_val_score(estimator, X_train, y_train, scoring = "neg_mean_squared_error", cv = kfold)).mean(), 5)
        R2 = round(cross_val_score(estimator, X_train, y_train, scoring = "r2", cv = kfold).mean(),5)
        
        print(f'Training model {estimator_name} for dataset {idx}')
        
    from mlxtend.regressor import StackingCVRegressor
    
    stack_reg = StackingCVRegressor(regressors = (forest, gboost, bagging, lgbm, xgbr), meta_regressor = lgbm, cv = kfold)
    stacker = stack_reg.fit(X_train, y_train);  
    
    def blender(X):
        return ((0.35 * stack_reg.predict(X)) +
            (0.25 * models['XGBRegressor'].predict(X)) +
            (0.15 * models['BaggingRegressor'].predict(X)) +  
            (0.25 * models['LGBMRegressor'].predict(X)))
    
    models['stacker'] = stacker
    
    model_dict[idx] = models

    pred = blender(X_val)
    blended_score = round(mean_squared_error(pred, y_val, squared = False),0)
    blended_score_r2 = round(r2_score(pred, y_val),5)
    
    print(f'MODEL NUMBER {idx}')
    print(f'Train set: {X_train.shape[0]}; {y_train.shape[0]}\nTest set: {X_test.shape[0]}; {y_test.shape[0]}\nValidation set: {X_val.shape[0]}; {y_val.shape[0]}')
    print(f'\nRMSE of the blender is {blended_score}\nr2 is {blended_score_r2}\n\n')
    
SAVE_MODEL_DICT = True

if SAVE_MODEL_DICT:
    
    import pickle
    with open('all_models_dict_v2.pickle', 'wb') as handle:
        pickle.dump(model_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)