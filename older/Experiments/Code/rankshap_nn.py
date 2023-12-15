#%%
import numpy as np
import sys
import pickle
import pathlib
from os.path import join
path_to_file = str(pathlib.Path().resolve())
dir_path = join(path_to_file, "../../")
# dir_path = "/accounts/grad/jeremy_goldwasser/RankSHAP"

sys.path.append(join(dir_path, "HelperFiles"))
from helper import *
from shapley_sampling2 import *
from train_models import *
from load_data import *

import warnings
warnings.filterwarnings('ignore')

dataset = sys.argv[1]
K = int(sys.argv[2])
fname = "shap_" + dataset + "_nn_K" + str(K) + "_10x"
print(fname)
X_train, y_train, X_test, y_test, mapping_dict = load_data(join(dir_path, "Experiments", "Data"), dataset)

model = train_neural_net(X_train, y_train)

#%%
np.random.seed(1)
N_runs = 500
N_pts = 10

shap_vals_all_pts = []
for i in range(N_pts):
    print(i)
    xloc = X_test[i:(i+1)]
    shap_vals_all = []
    top_K = []
    while len(top_K) < N_runs:
        shap_vals, _ = shapley_sampling_adaptive(model, X_train, xloc, K=K, alpha=0.2, 
                                mapping_dict=mapping_dict, max_n_perms=10000, n_init=100, n_equal=False)
        if isinstance(shap_vals, np.ndarray):
            #### Compute empirical FWER #####
            est_top_K = get_ordering(shap_vals)[:K]
            top_K.append(est_top_K)
            shap_vals_all.append(shap_vals)
            if len(top_K) % 20 == 0: # 20
                top_K_arr = np.array(top_K)
                most_common_row = mode_rows(top_K_arr)
                ct = 0
                for idx in range(len(top_K)):
                    if np.array_equal(most_common_row, top_K_arr[idx]):
                        ct += 1
                fwer = 1 - ct / len(top_K)
                print(len(top_K), np.round(fwer, 2)) # "FWER
    shap_vals_all_pts.append(shap_vals_all)

    # Store results
    with open(join(dir_path, "Experiments", "Results", fname), "wb") as fp:
        pickle.dump(shap_vals_all_pts, fp)

