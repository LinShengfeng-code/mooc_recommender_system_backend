# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: {}
# @Date: 2022/4/11 14:29
import numpy as np

from rec.ItemBasedCollaborativeFilter.itemBasedCF import itemBasedCF
from rec.TagBasedRatingSort.DataProcessing import getTrainTest
import matplotlib.pyplot as plt


if __name__ == '__main__':
    trainEnrollments, testEnrollments = getTrainTest()
    itemCF = itemBasedCF(trainEnrollments, testEnrollments)
    NList = [5, 10, 20, 50, 100]
    k = 5
    accList, recallList = [], []
    for n in NList:
        acc, recall = itemCF.test(k, n)
        accList.append(acc * 100)
        recallList.append(recall * 100)
        print('N={0}, k={1}, acc={2}, recall={3}'.format(n, k, acc, recall))
    plt.bar(np.arange(len(NList)), accList, tick_label=NList)
    plt.title('Accuracy of Different N')
    plt.xlabel('N')
    plt.ylabel('Accuracy (%)')
    plt.show()
    plt.bar(np.arange(len(NList)), recallList, tick_label=NList)
    plt.title('Recall of Different N')
    plt.xlabel('N')
    plt.ylabel('Recall (%)')
    plt.show()
