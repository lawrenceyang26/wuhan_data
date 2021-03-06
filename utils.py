import io
import os
import zipfile
import numpy as np
import pandas as pd


NUM_ONES_COL = 'num_ones'
NUM_ALL_COL  = 'num_all'
RISK_COL     = 'risk'

def readZipCSV(dir, fileName):
# TODO: make it a full-fledged data reader applicable to potential Kaggle projects
    baseName = os.path.splitext(fileName)[0]
    return pd.read_csv(io.TextIOWrapper(zipfile.ZipFile(dir+fileName).open(baseName,"rU")))

def printList(aList,format):
    for item in aList:
        print(format % (item),end="")
    print('\n')

def gen1DRiskTable(df,catVarName,targetVarName,targetValue):
    all = df.loc[:,catVarName].value_counts()
    ones = df.loc[df.loc[:,targetVarName]==targetValue,catVarName].value_counts()
    return pd.DataFrame({NUM_ONES_COL:ones,NUM_ALL_COL:all,RISK_COL:ones/all}).fillna(0)

def print1DRiskTable(rt,out):
    print(rt.sort(RISK_COL,ascending=False).to_string(),file=out)

def genRiskTable(df,catVarNameList,targetVarName):
    """
    Generates a hashtable with keys being the combination of catVarNameList and values being
    the estimated probability that the target is 1, assuming targetVarName is a binary variable.
    Example:
        rt = genRiskTable(df, ['colA','colB'], 'target')
        rt['colA_val1']
    """
    return df.groupby(catVarNameList)[targetVarName].mean()

def genCondProbTable(df,listA,listB):
    """
    Generate a hashtable with keys being the combination of the variables in listA+listB, and
    values being the estimated probability Pr(listA=a|listB=b). Both listA and listB can be
    a list of variable names.
    Example:
        cpt = genCondProbTable(df,['colA1','colA2'],['colB1','colB2'])
        cpt['colA1_val1','colA2_val2','colB1_val1','colB2_val2']
    """
    if not listA:
        print("ERROR: Can't calculate probabilities for an empty list of variables.")
        return None

    totals = df.groupby(listA+listB)[listA[0]].count()
    if listB:
        return totals.groupby(level=listB).apply(lambda s: s.astype(float)/s.sum())
    else:
        return totals/totals.sum()

def genCondProbVar(df,cpt):
    """
    Generate a variable/column based on a conditional probability table. The input dataframe df
    should contain column(s) whose values are keys to the conditional probability table.
    Example:
        aNewVar = genCondProbVar(df, cpt)
        df['anotherNewVar'] = genCondProbVar(df, cpt)
    """
    cols = cpt.index.names
    if len(cols) == 1:
        return df.loc[:,cols].apply(lambda row: cpt.get(row.values), axis=1)
    elif len(cols) >= 2:
        return df.loc[:,cols].apply(lambda row: cpt.get(tuple(row.values)), axis=1)
    else:
        print("ERROR: Empty conditional probability hash table.")
        return None

