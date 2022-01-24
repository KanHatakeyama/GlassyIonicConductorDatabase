from datetime import datetime as dt
import time
import pandas as pd
import numpy as np
import copy
import re
from string_parse import make_electrolyte_name

def search_corresponding_data_id(target_record, measurement_df, checksum_column):
    diff_records = abs(measurement_df-target_record)

    # search for records, having the same preparation date, donor/acceptor/salt ratio
    diff_records["checksum"] = diff_records["1st Day (unix)"]+diff_records["Formal donor ratio"] + \
        diff_records["Formal acceptor ratio"]+diff_records["Formal salt ratio"]
    diff_records = diff_records.sort_values(by=checksum_column)
    found_indices = diff_records[diff_records["checksum"]
                                 == 0].iloc[1:, :].index
    return found_indices


def add_unique_IDs(df, keys):
    anal_df = copy.copy(df)

    # check sealing conditions
    sealing_keys = [k for k in list(keys) if k.find("KitchenBoss") > 0]
    anal_df["Sealer"] = anal_df[sealing_keys].sum(axis=1)
    anal_df.loc[anal_df['Sealer'] >= 1, 'Sealer'] = 1

    # check anneal conditions
    anneal_keys = [k for k in list(keys) if k.find(
        "hot plate") > 0 or k.find("AMF-20N") > 0]
    anal_df["Anneal"] = anal_df[anneal_keys].sum(axis=1)
    anal_df["Anneal"][anal_df["Anneal"] >= 1] = 1

    interested_conditions = ["Donor MW", "Acceptor MW", "Salt MW",
                             "Formal D/A ratio", "Salt weight ratio", "Anneal", "Sealer"]

    anal_df = anal_df.sort_values(by="2nd Day (unix)", ascending=False)

    anal_df["manual condition"] = ""
    for col in interested_conditions:
        anal_df["manual condition"] = anal_df["manual condition"] + \
            ":"+anal_df[col].astype(float).round(2).astype(str)

    anal_df = anal_df.sort_values(by="manual condition", ascending=False)
    manual_cond_list = list(anal_df["manual condition"])

    anal_df["manual condition"] = [make_electrolyte_name(
        target_str) for target_str in manual_cond_list]

    return anal_df


# parse dataframe
def custom_df_parse(df):
    # custom data parsing
    df["Log ionic conductivity (S/cm)"] = df["ionic_conductivity_sigma"].str.replace(
        " S/cm", "").astype(float)
    df["Log ionic conductivity (S/cm)"] = np.log10(
        df["Log ionic conductivity (S/cm)"])

    df["Temperature of $\sigma$$_\mathrm{ion}$ ($^\mathrm{o}$C)"] = df["ionic_conductivity_temperature"].str.replace(
        " oC", "").astype(float)
    df["Temperature of $\sigma$$_\mathrm{ion}$ ($^\mathrm{o}$C)"] = df["Temperature of $\sigma$$_\mathrm{ion}$ ($^\mathrm{o}$C)"].fillna(
        25.01)

    df["Thickness ($\mu$m)"] = df["electrolyte_thickness_thickness"].str.replace(
        " um", "").astype(float)
    df["Donor amount (mg)"] = df["donor_amount_weight"].str.replace(
        " mg", "").astype(float)
    df["Acceptor amount (mg)"] = df["acceptor_amount_weight"].str.replace(
        " mg", "").astype(float)

    df["Donor MW"] = df["donor_amount_MW"].astype(float)
    df["Acceptor MW"] = df["acceptor_amount_MW"].astype(float)
    df["Salt MW"] = df["salt_amount_MW"].astype(float)

    df["CT complex yield (mg)"] = df["CT_complex_yield_weight"].str.replace(
        " mg", "").astype(float)
    df["CT complex amount (mg)"] = df["CT_complex_amount_weight"].str.replace(
        " mg", "").astype(float)
    df["Salt amount (mg)"] = df["salt_amount_weight"].str.replace(
        " mg", "").astype(float)
    df["O$_{2}$ (1st day) (ppm)"] = df["glove_box_condition1_O2"].str.replace(
        " ppm", "").astype(float)
    df["O$_{2}$ (2nd day) (ppm)"] = df["glove_box_condition2_O2"].str.replace(
        " ppm", "").astype(float)
    df["Dew point (1st day) ($^\mathrm{o}$C)"] = df["glove_box_condition1_Dew"].str.replace(
        " oC", "").astype(float)
    df["Dew point (2nd day) ($^\mathrm{o}$C)"] = df["glove_box_condition2_Dew"].str.replace(
        " oC", "").astype(float)

    # calculate donor/acceptor ratio
    temp_df = pd.DataFrame()
    temp_df["acceptor actual (mg)"] = df["CT complex yield (mg)"] - \
        df["Donor amount (mg)"]
    temp_df["acceptor actual (mol)"] = temp_df["acceptor actual (mg)"] / \
        df["Acceptor MW"]
    temp_df["donor actual (mol)"] = df["Donor amount (mg)"]/df["Donor MW"]
    temp_df["donor/(donor+acceptor)"] = df["Donor amount (mg)"] / \
        (df["Donor amount (mg)"]+temp_df["acceptor actual (mg)"])
    temp_df["donor added (mg)"] = df["CT complex amount (mg)"] * \
        temp_df["donor/(donor+acceptor)"]
    temp_df["acceptor added (mg)"] = df["CT complex amount (mg)"] * \
        (1-temp_df["donor/(donor+acceptor)"])
    temp_df["donor added (mol)"] = temp_df["donor added (mg)"]/df["Donor MW"]
    temp_df["acceptor added (mol)"] = temp_df["acceptor added (mg)"] / \
        df["Acceptor MW"]

    temp_df["salt (mol)"] = df["Salt amount (mg)"]/df["Salt MW"]
    temp_df["total (mol)"] = temp_df["salt (mol)"] + \
        temp_df["donor added (mol)"]+temp_df["acceptor added (mol)"]

    temp_df["donor_formal (mol)"] = df["Donor amount (mg)"]/df["Donor MW"]
    temp_df["acceptor_formal (mol)"] = df["Acceptor amount (mg)"] / \
        df["Acceptor MW"]
    temp_df["formal total (mol)"] = temp_df["salt (mol)"] + \
        temp_df["donor_formal (mol)"]+temp_df["acceptor_formal (mol)"]

    df["Donor ratio"] = temp_df["donor added (mol)"]/temp_df["total (mol)"]
    df["Acceptor ratio"] = temp_df["acceptor added (mol)"] / \
        temp_df["total (mol)"]
    df["Salt ratio"] = temp_df["salt (mol)"]/temp_df["total (mol)"]
    df["Salt ratio"] = df["Salt ratio"].fillna(1)

    df["Formal donor ratio"] = temp_df["donor_formal (mol)"] / \
        temp_df["formal total (mol)"]
    df["Formal acceptor ratio"] = temp_df["acceptor_formal (mol)"] / \
        temp_df["formal total (mol)"]

    df["Formal D/A ratio"] = temp_df["donor_formal (mol)"]/(
        temp_df["acceptor_formal (mol)"]+temp_df["donor_formal (mol)"])
    df["Formal D/A ratio"] = df["Formal D/A ratio"].fillna(0)

    df["Formal salt ratio"] = temp_df["salt (mol)"] / \
        temp_df["formal total (mol)"]
    df["Formal salt ratio"] = df["Formal salt ratio"].fillna(1)

    df["Formal donor ratio"] = df["Formal donor ratio"].fillna(0)
    df["Formal acceptor ratio"] = df["Formal acceptor ratio"].fillna(0)

    df["Salt weight ratio"] = df["Salt amount (mg)"]/(
        df["CT complex amount (mg)"]+df["Salt amount (mg)"])
    df["Salt weight ratio"] = df["Salt weight ratio"].fillna(1)

    # calculate dsc info
    df["DSC (salt_melting_temperature)"] = df["DSC_salt_melt_temp"].str.replace(
        " oC", "").astype(float)
    df["DSC (salt_melting_heat_energy)"] = df["DSC_salt_melt_heat"].str.replace(
        " J/g", "").astype(float)

    df["DSC (sample amount)"] = df["DSC_sample_amount"].str.replace(
        " mg", "").astype(float)

    # convert to unix time
    def striptime(s):
        try:
            return dt.strptime(s, '%Y/%m/%d')
        except:
            return "0/0/0"

    def unixtime(d):
        try:
            return int(time.mktime(d.timetuple()))
        except:
            return -1

    temp_df["Day1"] = df["glove_box_condition1_Day"].apply(striptime)
    df["1st Day (unix)"] = temp_df["Day1"].apply(unixtime)
    temp_df["Day2"] = df["glove_box_condition2_Day"].apply(striptime)
    df["2nd Day (unix)"] = temp_df["Day2"].apply(unixtime)

    df["Date difference"] = df["2nd Day (unix)"]-df["1st Day (unix)"]

    df = custom_df_parse2(df)

    df = df.rename(columns={'cell_id_cell_id': "Cell ID"})

    del_list = ["donor_amount_MW",
                "acceptor_amount_MW",
                "salt_amount_MW",
                ]
    df = df.drop(del_list, axis=1)

    return df

# parse dataframe


def custom_df_parse2(df):
    # analyze ball mill data
    ball_mill_columns = [
        i for i in df.columns if i.find("Ball mill, type:") > 0]
    ball_mill_time_dict = {
        k: float(re.findall(r'time: (\d*) min', k)[0]) for k in ball_mill_columns}

    ball_mill_time_label = "Total ball mill time (min)"
    df[ball_mill_time_label] = 0.0

    for col in ball_mill_time_dict:
        # print(col)
        df[ball_mill_time_label] = (
            df[ball_mill_time_label])+(df[col])*ball_mill_time_dict[col]
        # print(df[ball_mill_time_label][5])

    heat_columns = [i for i in df.columns if i.find(
        "Heat, type: procedure") > 0]
    heat_columns = [i for i in heat_columns if i.find("Seal") < 0]
    heat_columns = [i for i in heat_columns if i.find("AMF-20N") < 0]

    #heat_temp_dict={k:float(re.findall(r'temperature: (\d*) oC', k)[0]) for k in heat_columns}
    heat_time_dict = {
        k: float(re.findall(r'time: (\d*) min', k)[0]) for k in heat_columns}

    heat_time_label = "Total heat time (min)"
    df[heat_time_label] = 0.0

    for col in heat_time_dict:
        # print(col)
        df[heat_time_label] = (df[heat_time_label]) + \
            (df[col])*heat_time_dict[col]
        # print(df[ball_mill_time_label][5])

    for col in list(df.columns):
        try:
            df[col] = df[col].astype(float)
        except:
            pass

    return df



# make dataframe for imputed data
def prepare_custom_imputed_dataframe(anal_df, num_df, num_temp_df, imputed_df, cond_label):
    nan_pos = np.where(np.array(num_temp_df.values) !=
                       np.array(num_temp_df.values))

    imputed_array = np.array(imputed_df.drop(cond_label, axis=1))
    integrated_array = np.array(num_temp_df)
    integrated_array = np.round(integrated_array).astype(str)

    for i, j in zip(nan_pos[0], nan_pos[1]):
        v = str("{:.2f}".format(imputed_array[i][j]))
        integrated_array[i][j] = "("+v+")"

    integrated_imputed_df = copy.copy(imputed_df.drop(cond_label, axis=1))
    integrated_imputed_df.iloc[:, :] = integrated_array
    integrated_imputed_df[cond_label] = num_df[cond_label]

    integrated_imputed_df = integrated_imputed_df[integrated_imputed_df[cond_label]
                                                  == integrated_imputed_df[cond_label]]
    #target_columns=[i for i in integrated_imputed_df.columns if i.find("label:")==-1 and i.find("FP")==-1]
    target_columns = integrated_imputed_df.columns

    integrated_imputed_df = integrated_imputed_df[target_columns]
    integrated_imputed_df["manual condition"] = anal_df["manual condition"]
    return integrated_imputed_df


# calculate median and std of conductivity for same electrolytes
def prepare_group_score_df(df, cond_label, all_fp_keys):
    temp_sigma_df = df[df[cond_label] == df[cond_label]]
    temp_anal_df = add_unique_IDs(temp_sigma_df, all_fp_keys)
    temp_anal_df = temp_anal_df[temp_anal_df[
        "Temperature of $\sigma$$_\mathrm{ion}$ ($^\mathrm{o}$C)"] == 25.01]

    group_score_df = temp_anal_df.groupby("manual condition").median()
    group_std_df = temp_anal_df.groupby("manual condition").std()

    group_score_df[cond_label] = group_score_df[cond_label] - \
        group_std_df[cond_label]
    group_score_df = group_score_df[group_score_df[cond_label]
                                    == group_score_df[cond_label]]
    group_score_df = group_score_df.reset_index()
    group_score_df = group_score_df.sort_values(by=cond_label)

    return group_score_df
