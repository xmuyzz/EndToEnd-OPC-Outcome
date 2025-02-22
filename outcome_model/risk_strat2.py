import os
import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts
import matplotlib.pyplot as plt
from lifelines.utils import median_survival_times
from lifelines.statistics import logrank_test
from lifelines.statistics import multivariate_logrank_test
from time import localtime, strftime
from sklearn.cluster import KMeans
from opts import parse_opts
from sklearn.preprocessing import StandardScaler
from lifelines import CoxPHFitter


def risk_strat(opt, task, cox_type, hpv, n_group, surv_type, cluster_model, random_state, surv_csv):

    def get_data(dataset):
        data_dir = task_dir + '/' + dataset
        save_dir = task_dir + '/' + dataset + '/' + cox_variable
        
        fn = dataset + '_img_label_' + opt.tumor_type + '.csv'
        df = pd.read_csv(data_dir + '/' + fn)
        times, events = surv_type + '_time', surv_type + '_event'
        df = df.dropna(subset=[times, events])

        if surv_csv == 'raw':
            surv_fn = 'raw_surv_2.csv'
        elif surv_csv == 'full':
            surv_fn = 'full_surv_2.csv'   
        surv = pd.read_csv(save_dir + '/' + surv_fn)

        # # subgroup analysis based on HPV status
        # if hpv == 'hpv+':
        #     df = df.loc[df['HPV'].isin([1])]
        #     #df0 = df0.loc[df0['hpv'].isin([1])]
        #     print('patient n = ', df.shape[0])
        # elif hpv == 'hpv-':
        #     df = df.loc[df['HPV'].isin([0])]
        #     #df0 = df0.loc[df0['hpv'].isin([0])]
        #     print('patient n = ', df.shape[0])
        # elif hpv == 'hpv':
        #     # patients with known HPV status
        #     df = df.loc[df['HPV'].isin([0, 1])]
        #     #df0 = df0.loc[df0['hpv'].isin([0, 1])]
        #     print('patient n = ', df.shape[0])
        # elif hpv == 'all':
        #     print('\npatient n = ', df.shape[0])

        print('clustering patients into 3 risk groups')

        if cluster_model == 'clinical':
            df3 = df[['Female', 'Age>65', 'Smoking>10py', 'T-Stage-1234', 'N-Stage-0123']]
        elif cluster_model == 'dl_clinical':
            df3 = surv.T
            df3.columns = ['time1', 'time2', 'time3', 'time4', 'time5', 'time6', 'time7', 'time8', 'time9', 'time10']
            df3 = df3.reset_index()
            df2 = df[['Age>65', 'Female', 'T-Stage-1234', 'N-Stage-0123', 'Smoking>10py']].reset_index()
            df3 = pd.concat([df3, df2], axis=1)
            print('df3:', df3)
        elif cluster_model == 'dl_clinical_muscle':
            df3 = surv.T
            df3.columns = ['time1', 'time2', 'time3', 'time4', 'time5', 'time6', 'time7', 'time8', 'time9', 'time10']
            df3 = df3.reset_index()
            df2 = df[['Age>65', 'Female', 'T-Stage-1234', 'N-Stage-0123', 'Smoking>10py', 'Muscle_Area', 'Muscle_Density']].reset_index()
            df3 = pd.concat([df3, df2], axis=1)
            print('df3:', df3)
        elif cluster_model == 'dl_clinical_adipose':
            df3 = surv.T
            df3.columns = ['time1', 'time2', 'time3', 'time4', 'time5', 'time6', 'time7', 'time8', 'time9', 'time10']
            df3 = df3.reset_index()
            df2 = df[['Age>65', 'Female', 'T-Stage-1234', 'N-Stage-0123', 'Smoking>10py', 'Adipose_Area', 'Adipose_Density']].reset_index()
            df3 = pd.concat([df3, df2], axis=1)
            print('df3:', df3)       
        elif cluster_model == 'dl_clinical_muscle_adipose':
            df3 = surv.T
            df3.columns = ['time1', 'time2', 'time3', 'time4', 'time5', 'time6', 'time7', 'time8', 'time9', 'time10']
            df3 = df3.reset_index()
            df2 = df[['Age>65', 'Female', 'T-Stage-1234', 'N-Stage-0123', 'Smoking>10py', 'Muscle_Area', 
                'Muscle_Density', 'Adipose_Area', 'Adipose_Density']].reset_index()
            df3 = pd.concat([df3, df2], axis=1)
            print('df3:', df3)
        elif cluster_model == 'tot':
            df_surv = surv.T
            df_surv.columns = ['prob_score'] * surv.shape[0]
            df_surv = df_surv.reset_index()
            df_clinical = df[[times, events, 'Age>65', 'Female', 'T-Stage-1234', 'N-Stage-0123', 'Smoking>10py', 'Muscle_Area', 
                    'Muscle_Density', 'Adipose_Area', 'Adipose_Density']].reset_index()
            df_tot = pd.concat([df_surv, df_clinical], axis=1)
            df_tot.dropna(inplace=True)
            #print('df_tot:', df_tot)
        elif cluster_model == 'dl':
            df_surv = surv.T
            df_surv.columns = ['prob_score'] * surv.shape[0]
            df_surv[times] = df[times].to_list()
            df_surv[events] = df[events].to_list()
            df_surv.dropna(inplace=True)
            df_tot = df_surv
            #print('df_tot:', df_tot)
        return df_tot
    

    def plot(x, y, df, save_dir):
        times, events = surv_type + '_time', surv_type + '_event'
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.scatter(x[:, 0], x[:, 1], c=y, s=50, cmap='viridis')
        centers = k_means.cluster_centers_
        plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)
        plt.savefig(save_dir + '/clustering.png', format='png', dpi=300)
        plt.close() 
        print('save clustering figure')

        # multivariate log-rank test for 3 risk groups
        results = multivariate_logrank_test(df[times], df['group'], df[events])
        #results.print_summary()
        p_value = np.around(results.p_value, 8)
        print('log-rank test p-value:', p_value)
        #print(results.test_statistic)

        # 5-year survival rates for 3 risk groups
        dfs = []
        for i in range(n_group):
            df3 = df.loc[df['group'] == i]
            print('df:', i, df3.shape[0])
            dfs.append(df3)
            #print('df0:', dfs)

        # 5-year OS for subgroups
        for i in range(n_group):
            ls_event = []
            for time, event in zip(dfs[i][times], dfs[i][events]):
                if time <= 1825 and event == 1:
                    event = 1
                    ls_event.append(event)
            #print('dfs[i]:', dfs[i])
            os_5yr = round(1 - len(ls_event)/dfs[i].shape[0], 3)
            print('5-year survial rate:', i, os_5yr)

        # Kaplan-Meier plots for 3 risk groups 
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        labels = ['I', 'II', 'III']
        #labels = ['Low risk', 'High risk', 'Intermediate risk']
        #dfs = [df0, df1, df2]
        for df, label in zip(dfs, labels):
            kmf = KaplanMeierFitter()
            #print(df[times])
            #print(df[events])
            #print('df:', df)
            kmf.fit(df[times], df[events], label=label)
            #kmf.fit(df['rfs_time'], df['rfs_event'], label=label)
            ax = kmf.plot_survival_function(ax=ax, show_censors=True, ci_show=True) #,censor_style={"marker": "o", "ms": 60})
            #add_at_risk_counts(kmf, ax=ax)
            median_surv = kmf.median_survival_time_
            median_surv_CI = median_survival_times(kmf.confidence_interval_)
            print('median survival time:', median_surv)
            #print('median survival time 95% CI:\n', median_surv_CI)
        
        plt.xlabel('Time (days)', fontweight='bold', fontsize=12)
        plt.ylabel('Survival probability', fontweight='bold', fontsize=12)
        plt.xlim([0, 5000])
        plt.ylim([0, 1.05])
        #ax.patch.set_f66acecolor('gray')
        ax.axhline(y=0, color='k', linewidth=2)
        ax.axhline(y=1.05, color='k', linewidth=2)
        ax.axvline(x=0, color='k', linewidth=2)
        ax.axvline(x=5000, color='k', linewidth=2)
        # ax.spines['top'].set_visible(False)
        # ax.spines['right'].set_visible(False)
        plt.xticks([0, 1000, 2000, 3000, 4000, 5000], fontsize=12, fontweight='bold')
        plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0], fontsize=12, fontweight='bold')
        plt.legend(loc='lower left', prop={'size': 12, 'weight': 'bold'})
        #plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc='lower left', mode="expand", 
        #           borderaxespad=0, ncol=3, prop={'size': 12, 'weight': 'bold'})
        plt.grid(True)
        #plt.title('Log-Rank Test: p = %s' % p_value, fontsize=16, fontweight='bold')
        plt.tight_layout(pad=1.08, h_pad=None, w_pad=None, rect=None)
        plt.savefig(save_dir + '/Kaplan_Meier.jpg', format='png', dpi=300)
        plt.close()
        print('saved Kaplan-Meier curve!')
        return fig
    
    
    task_dir = opt.proj_dir + '/task/' + task + '_' + surv_type + '_' + opt.img_size + '_' + \
               opt.img_type + '_' + opt.tumor_type + '_' + opt.cox + '_' + opt.cnn_name + str(opt.model_depth) 

    df_va = get_data('va2')
    df_ts = get_data('ts2')
    df_tx1 = get_data('tx_maastro')
    df_tx2 = get_data('tx_bwh')

    #x = df.drop(columns=[surv_type + '_time', surv_type + '_event']).values
    x_va = StandardScaler().fit_transform(df_va.values)
    x_ts = StandardScaler().fit_transform(df_ts.values)
    x_tx1 = StandardScaler().fit_transform(df_tx1.values)
    x_tx2 = StandardScaler().fit_transform(df_tx2.values)
    
    k_means = KMeans(n_clusters=n_group, copy_x=True, 
                     init='k-means++', n_init='auto', 
                     max_iter=500,
                     random_state=random_state, 
                     tol=0.0001, verbose=0)
    k_means.fit(x_va)

    y_va = k_means.predict(x_va)
    y_ts = k_means.predict(x_ts)
    y_tx1 = k_means.predict(x_tx1)
    y_tx2 = k_means.predict(x_tx2)
    df_va['group'] = y_va
    df_ts['group'] = y_ts
    df_tx1['group'] = y_tx1
    df_tx2['group'] = y_tx2

    xs = [x_va, x_ts, x_tx1, x_tx2]
    ys = [y_va, y_ts, y_tx1, y_tx2]
    dfs = [df_va, df_ts, df_tx1, df_tx2]
    datasets = ['va2', 'ts2', 'tx_maastro', 'tx_bwh']

    for x, y, df, dataset in zip(xs, ys, dfs, datasets):
        save_dir = task_dir + '/' + dataset + '/' + cox_variable
        plot(x, y, df, save_dir)

    
if __name__ == '__main__':

    opt = parse_opts()

    task = 'Task053'
    surv_type = 'os'
    n_group = 3
    cluster_model = 'dl'
    random_state = 42
    hpv = 'all'
    surv_csv = 'raw'
    cox_type = 'PCHazard'
    cox_variable = 'tot'

    risk_strat(opt, task, cox_type, hpv, n_group, 
               surv_type, cluster_model, random_state, 
               surv_csv)