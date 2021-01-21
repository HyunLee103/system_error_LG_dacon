import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import os

from tqdm import tqdm
import gc
import random
import lightgbm as lgb
import re
from sklearn.metrics import *
from sklearn.model_selection import KFold
import warnings
warnings.filterwarnings(action='ignore')


def f_pr_auc(probas_pred, y_true):
    labels=y_true.get_label()
    p, r, _ = precision_recall_curve(labels, probas_pred)
    score=auc(r,p) 
    return "pr_auc", score, True

def mk_err_feature(df,user_num,user_min):
    # errtype
    id_error = df[['user_id','errtype']].values
    error = np.zeros((user_num,42))

    for person_idx, err in tqdm(id_error):
        error[person_idx - user_min,err - 1] += 1

    # model_nm
    id_model = df[['user_id','model_nm']].values
    model = np.zeros((user_num,9))

    for idx, mol_nm in tqdm(id_model):  
        model[idx-user_min,int(mol_nm[-1])-1] += 1

    # errcode
    # df.errcode.value_counts()[df.errcode.value_counts()>100000].keys()
    errcode_top14 = ['1', '0', 'connection timeout', 'B-A8002', '80', '79', '14', 'active','2', '84', '85', 'standby', 'NFANDROID2','connection fail to establish']
    id_code = df[['user_id','errcode']].values
    code_df = np.zeros((user_num,14))

    for idx, code in tqdm(id_code):
        if code in errcode_top14:
            code_df[idx-user_min,errcode_top14.index(code)] += 1
        else:
            pass

    return np.concatenate((error,model,code_df),axis=1)

    

def mk_qt_feature(df,vars,user_num,user_min):
    q1 = np.zeros((user_num,5))
    q2 = np.zeros((user_num,5))
    for i, var in enumerate(vars):
        id_q = df[['user_id',var]].values
        res = np.zeros((user_num,5))

        for idx, num in tqdm(id_q):
            if num == 0:
                res[int(idx)-user_min,0] += 1
            elif num == -1:
                res[int(idx)-user_min,1] += 1
            elif num == 1:
                res[int(idx)-user_min,2] += 1
            elif num == 2:
                res[int(idx)-user_min,3] += 1
            else:
                res[int(idx)-user_min,4] += 1

        # 0,1,2,6,8,11,12 거의 비슷, 5,7,9,10 거의 비슷, 각각 평균 내서 사용
        if i in [0,1,2,4,6,9,10]:
            q1 += res
        else:
            q2 += res
    
    return np.concatenate((q1/7,q2/4),axis=1)