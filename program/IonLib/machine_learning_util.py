import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt


from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor

def auto_evaluation(selected_reg_df,cond_label,model = RandomForestRegressor()):
    tr_df, te_df = train_test_split(selected_reg_df, test_size=0.2)
    X = selected_reg_df.drop(cond_label, axis=1)
    y = selected_reg_df[[cond_label]]

    tr_X = tr_df.drop(cond_label, axis=1)
    tr_y = tr_df[[cond_label]]
    te_X = te_df.drop(cond_label, axis=1)
    te_y = te_df[[cond_label]]

    
    model.fit(tr_X, tr_y)

    tr_pred_y = model.predict(tr_X)
    print("train R2: ", r2_score(tr_y, tr_pred_y))
    te_pred_y = model.predict(te_X)
    print("test R2: ",r2_score(te_y, te_pred_y))

    vmin, vmax = -12, -2

    plt.figure(figsize=(5, 5), dpi=100)
    plt.xlim(vmin, vmax)
    plt.ylim(vmin, vmax)
    plt.yticks(np.arange(vmin, vmax, step=3))
    plt.xticks(np.arange(vmin, vmax, step=3))
    plt.xlabel("Log $\sigma_\mathrm{ion,exp}$ (S/cm)")
    plt.ylabel("Log $\sigma_\mathrm{ion,pred}$ (S/cm)")
    plt.rcParams["font.size"] = 20

    plt.scatter(tr_y, tr_pred_y, s=32, alpha=0.7, label="Train")
    plt.scatter(te_y, te_pred_y, s=32, alpha=0.7, label="Test")
    plt.plot((vmin, vmax), (vmin, vmax), c="black", alpha=0.3, linewidth=1)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left',
               borderaxespad=0, fontsize=18)