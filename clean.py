import pandas as pd
import numpy as np



def handleUncertain(data, log, report):
    temp = report["uncertain"].copy()
    for i in temp:
        data[i] = data[i].str.strip().replace('', np.nan)
        data[i] = data[i].apply(pd.to_numeric, errors='coerce')
        if data[i].isna().sum() == len(data):
            data = data.drop(i, axis=1)
            log.append("Dropped column " + i + " due to uncertainity")
        else:
            report[i] = {}
            report[i]['na'] = data[i].isna().sum() / len(data)
            report[i]['type'] = "num"
            report["uncertain"].remove(i)
            log.append("Modified report to accomodate " + i)
    return data, log, report

    # data = data.drop(i, axis=1)
    # log.append("Dropped " + i + "due to uncertainity")


def clean(data, to_drop=[], na_thresh=0.25, percofcat=0.25, encode_cat=True, drop_rows_if_needed=True, num_interpolate="mean"):
    log = []
    encodings = {}
    for i in to_drop:
        data = data.drop(i, axis=1)
        log.append("Dropped column " + i + " as requested")

    report = getStats(data, percofcat)
    if report["uncertain"]:
        data, log, report = handleUncertain(data, log, report)
        report.pop("uncertain")
        print("uncertain" in report)
    # print(report, "\n\n")

    for i in report:
        # print(i)
        if report[i]["na"] >= na_thresh :
            '''If column is empty beyond limits, remove it'''
            data = data.drop(i, axis=1)
            log.append("Dropped column " + i + " as Na ratio: " + str(report[i]["na"]) + " > " + str(na_thresh))



        elif report[i]["type"] == 'num' and report[i]["na"] < na_thresh :
            '''If numerical and empty within limits, interpolate'''\

            if num_interpolate == "mean":
                '''Interpolate with mean'''
                data[i] = data[i].fillna(data[i].mean())

            if num_interpolate == "median":
                '''Interpolate with median'''
                data[i] = data[i].fillna(data[i].median())

            log.append(i + " : replaced Na with " + num_interpolate)


        elif report[i]["type"] == 'cat' and report[i]["na"] < na_thresh :
            '''If categorical and empty within limits, ...'''
            log.append(i + " has Na percentage of " + str(report[i]["na"]) + " < " + str(na_thresh) + " but is categorical.")

        elif report[i]["type"] == 'cat' and encode_cat:
            '''If categorical and not empty, encode it'''
            encodings[i] = getEncodings(data[i])
            log.append("Encoded column " + i)

    if drop_rows_if_needed:
        data1 = data.dropna()
        shape1 = data.shape
        shape2 = data1.shape
        log.append("Dropped " + str(shape1[0] - shape2[0]) + " rows")
        data = data1

    data = data.replace(encodings)


    return data, log, encodings


def getEncodings(o):
    o = list(set(o))
    o = sorted(o)
    enc = {cls: ind for ind, cls in enumerate(o)}
    return enc

def getStats(data, percofcat=0.25):
    cols = data.columns
    report = {}
    report['uncertain'] = []
    for i in cols:
        if "unique" in str(data[i].describe()):
            '''If categorical'''
            if len(data[i].unique()) <  percofcat * len(data):
                '''If number of categories are within limits'''
                report[i] = {}
                report[i]["na"] = data[i].isna().sum() / len(data)
                report[i]["type"] = "cat"
                report[i]["uniq"] = data[i].unique()
                report[i]["uniq_no"] = len(data[i].unique())
            else:
                '''Categorical but too many categories'''
                report["uncertain"].append(i)
        else:
            '''If numerical'''
            report[i] = {}                              # Numerical
            report[i]["na"] = data[i].isna().sum() / len(data)
            report[i]["type"] = "num"
    return report




