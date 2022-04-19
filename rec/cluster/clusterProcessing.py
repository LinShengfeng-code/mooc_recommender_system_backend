# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: {聚类}
# @Date: 2022/3/28 20:53
import numpy
import numpy as np

from rec.cluster.dataProcessing import *
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from rec.TagBasedRatingSort.DataProcessing import getSet


def getKMeansEstimator(trainList=None, n_clusters=23, init='random'):
    if not trainList:
        trainList = list(getUserFeatureDict().values())
    fitData = trainList  # 直接把训练数据读取进来
    kMeansEstimator = KMeans(n_clusters=n_clusters, init=init)
    kMeansEstimator.fit(fitData)
    return kMeansEstimator


def saveCenters(kMeansEstimator: KMeans):
    """
    :type kMeansEstimator: KMeans
    """
    centers = kMeansEstimator.cluster_centers_
    centerFilePath = 'centers/centers.txt'
    with open(centerFilePath, 'w+') as cf:
        def array2str(arr):
            string = ''
            for i in range(len(arr)):
                string += str(arr[i])
                if i < len(arr) - 1:
                    string += ' '
                else:
                    string += '\n'
            return string

        for center in centers:
            cf.write(array2str(center))


def loadCenters(fPath, n):
    centers = []
    with open(fPath, 'r') as f:
        centers = f.readlines()
        for i in range(len(centers)):
            c = centers[i][:-1].split(' ')
            centers[i] = [float(data) for data in c]
    centers = numpy.array(centers)
    kMeansEstimator = KMeans(init=centers, n_clusters=n, n_init=1)
    kMeansEstimator.fit([[0 for i in range(23)] for j in range(23)])
    return kMeansEstimator


def plotCenters(participants, kMeansEstimator: KMeans, colorName='r'):
    sub = ['创业', '电子', '工程', '公共管理', '化学', '环境·地球', '计算机', '建筑', '教育', '经管·会计', '历史', '汽车', \
           '社科·法律', '生命科学', '数学', '外语', '文学', '物理', '医学·健康', '艺术·设计', '哲学', '职场', '其他']
    centers = kMeansEstimator.cluster_centers_
    for c in range(len(centers)):
        if participants[c] > 0:
            plt.figure(figsize=(6, 8))
            plt.barh(y=np.arange(23), width=centers[c], height=0.5, tick_label=sub, color=colorName)
            plt.title('{0}簇之{1}, 人数{2}'.format(len(centers), c + 1, participants[c]))
            plt.show()


def statisticParticipants(kMeansEstimator: KMeans, trainList=None):
    sub = [str(j + 1) for j in range(len(kMeansEstimator.cluster_centers_))]
    r = kMeansEstimator.predict(trainList)
    participants = [0 for i in range(len(kMeansEstimator.cluster_centers_))]
    for i in r:
        participants[r[i]] += 1
    plt.bar(sub, participants, width=1.0)
    plt.title('各类别的人数')
    for k in range(len(kMeansEstimator.cluster_centers_)):
        plt.text(x=k - 0.3, y=participants[k] + 300, s=participants[k])
    plt.show()
    return participants


if __name__ == '__main__':
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    # 聚类
    # trainSet = list(getUserFeatureDict().values())
    trainSet = list(getUserFeatureDict(trainSet=getSet('../Data/mooc.all.rating.transfer')).values())
    estimator = getKMeansEstimator(n_clusters=23, trainList=trainSet)
    print(estimator.predict(trainSet))
    saveCenters(estimator)
    # participantsList = statisticParticipants(estimator, trainSet)
    # plotCenters(participantsList, estimator)
    """
    l = [i for i in range(3, 27, 2)]
    colorList = ['r', 'g', 'b', 'orange', 'purple', 'brown']
    sl = []
    d = []
    for i in l:
        estimator = getKMeansEstimator(trainSet, n_clusters=i)
        s = silhouette_score(trainSet, estimator.predict(trainSet))
        td = estimator.inertia_
        sl.append(s)
        d.append(td)
        plotCenters(estimator, colorName=colorList[((i - 3)//2) % len(colorList)])
        print('n_cluster: {0}, silhouette_score: {1}, inertia_: {2}'.format(i, s, td))
    # draw silhouette score intention
    plt.plot(l, sl, marker='o')
    plt.xlabel('N clusters')
    plt.ylabel('silhouette score')
    plt.title('silhouette score of different N')
    plt.show()
    # draw distortions intention
    plt.plot(l, d, marker='o')
    plt.xlabel('N clusters')
    plt.ylabel('distortions')
    plt.title('distortions of different N')
    plt.show()
    """
