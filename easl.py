#!/bin/python
# -*- coding: utf-8 -*-

import os,sys
import csv
import random
import numpy as np

np.random.seed(12345) 
random.seed(12345)

class EASL:
    """
    Efficient Annotation for Scalar Labels
    """

    def __init__(self, params):
        self.params = params
        self.items = {}
        self.headerModel = []
        self.headerHits = []
        print("model parameters")
        print(self.params)

    def loadItem(self, filePath):
        csvReader = csv.DictReader(open(filePath, 'r'))
        self.headerModel = csvReader.fieldnames
        for _h in self.headerModel:
            for _i in range(1, self.params["param_items"]+1):
                self.headerHits.append(_h + str(_i))

        for row in csvReader:
            self.items[row["id"]] = row

    def saveItem(self, newModelPath):
        csvWriter = csv.DictWriter(open(newModelPath, 'w', newline=''), fieldnames=self.headerModel)
        csvWriter.writeheader()
        for row in self.items.values():
            csvWriter.writerow(row)

    def generateHits(self, filePath, hitItems):
        csvWriter = csv.DictWriter(open(filePath, 'w', newline=''), fieldnames=self.headerHits)
        csvWriter.writeheader()

        for itemID, compareIDs in hitItems.items():
            ids = [itemID] + list(compareIDs)
            random.shuffle(ids)
            rowDict = {}

            for i, id_i in enumerate(ids):
                for headerItem in self.headerModel:
                    rowDict[headerItem + str(i+1)] = self.items[id_i][headerItem]
            csvWriter.writerow(rowDict)

    def getNextK(self, k, iterNum):
        kItems = {}

        if iterNum == 0:
            # The first iteration will cover all items.
            idList = []
            for itemID, row in self.items.items():
                idList.append(itemID)
            random.shuffle(idList)
            residual = self.params["param_items"] - (len(idList) % self.params["param_items"])
            idList = idList + idList[:residual]
            assert len(idList) % self.params["param_items"] == 0

            for sublist in zip(*[iter(idList)] * self.params["param_items"]):
                kItems[sublist[0]] = np.array(sublist[1:])

        else:
            # 1. select k different items according to variance
            varList = []    # [(itemID, var), (itemID, var), ...]
            indexSet = set([])

            for itemID, row in self.items.items():
                varList.append((row["id"], float(row["var"])))
                indexSet.add(itemID)

            varList = sorted(varList, key=lambda x:(-x[1], x[0]))
            kItemList = varList[:k]

            for _k in kItemList:
                indexSet.remove(_k[0]) # remove the item itself

            # 2. for each k, choose m items according to matching quality
            for _k in kItemList:
                _j = _k[0]  # itemID
                candidateID = []
                candidateProb = []
                sumProb = 0.
                m_j = float(self.items[_j]["mode"])
                var_j = float(self.items[_j]["var"])
                param_gamma = float(self.params["param_match"])

                for _i in indexSet:
                    m_i = float(self.items[_i]["mode"])
                    var_i = float(self.items[_i]["var"])
                    csq = 2. * param_gamma**2 + var_j + var_i
                    matchQuality = np.sqrt(2.0 * param_gamma**2 / csq) * np.exp( -((m_j - m_i)**2) / (2.0 * csq))
                    sumProb += matchQuality
                    candidateID.append(_i)
                    candidateProb.append(matchQuality)

                candidateProb = [p/sumProb for p in candidateProb]
                selectedIDs = np.random.choice(candidateID, self.params["param_items"]-1, p=candidateProb, replace=False)
                kItems[_j] = selectedIDs

                #print("##########################")
                #candidateProb.sort(reverse=True)
                #print(candidateProb)
                #print("########## ITEM ##########")
                #print(self.items[_j])
                #print("####### COMPARISON #######")
                #for _i in selectedIDs:
                #    print(self.items[_i])

        return kItems

    def alpha_from_beta(self, b, m):
        # compute alpha from beta (b) and mode (m)
        if m==1.0 or m==0.0 or b<=1:
            print("undefined")
            exit(1)
        return m/(1.-m)*b - (2.0*m-1.)/(1.-m)

    def beta_from_alpha(self, a, m):
        # compute beta from alpha (a) and mode (m)
        if m==1.0 or m==0.0 or a<=1:
            print("undefined")
            exit(1)
        return (1.-m)*a/m - (1.-2.*m)/m

    def alpha_beta_from_mode_sum(self, m, S):
        # compute alpha and beta from mode and sum of alpha+beta
        alpha = m * (S - 2.) + 1.
        beta = S - (S - 2.) * m - 1.
        assert alpha + beta == S
        return alpha, beta

    def mode(self, alpha, beta):
        alpha, beta = float(alpha), float(beta)
        if alpha == 1. and beta == 1.:
            return 0.5
        else:
            assert alpha + beta > 2.0
            if alpha < 1.0 and beta < 1.0:
                print("Error: alpha={}, beta={}".format(str(alpha), str(beta)))
                exit(1)
            return (alpha - 1.0) / (alpha + beta - 2.0)

    def mean(self, alpha, beta):
        alpha, beta = float(alpha), float(beta)
        return alpha / (alpha + beta)

    def variance(self, alpha, beta):
        alpha, beta = float(alpha), float(beta)
        return (alpha * beta) / ((np.power(alpha + beta, 2.0)) * (alpha + beta + 1))

    def observe(self, observe_path):
        csvReader = csv.DictReader(open(observe_path, 'r'))
        for row in csvReader:
            for _i in range(1, self.params["param_items"]+1):
                id_i = row["Input.id{}".format(_i)]
                s_i = float(row["Answer.range{}".format(_i)])/100.
                self.items[id_i]["alpha"] = float(self.items[id_i]["alpha"]) + s_i
                self.items[id_i]["beta"] = float(self.items[id_i]["beta"]) + (1. - s_i)
                self.items[id_i]["mode"] = self.mode(self.items[id_i]["alpha"], self.items[id_i]["beta"])
                self.items[id_i]["var"] = self.variance(self.items[id_i]["alpha"], self.items[id_i]["beta"])

