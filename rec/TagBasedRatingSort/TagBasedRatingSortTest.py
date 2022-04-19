# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 算法设计与测试 }
# @Date: 2022/3/22 15:23
from DataProcessing import getTrainTest
from web.models import *
from matplotlib import pyplot as plt
from rec.cluster.clusterProcessing import getKMeansEstimator
import numpy as np
from rec.AutoRec.RunAutoRec import getAutoRecModel
from rec.ItemBasedCollaborativeFilter.itemBasedCF import itemBasedCF


def loadCourseTypeDict():
    courseTypeDic = dict()
    for course in Course.objects.filter():
        courseTypeDic[course.id] = course.type
    return courseTypeDic


def train(trainSet):
    for record in trainSet:
        if userFeatureVectorDict.get(record[0], 0) == 0:  # 用户种类向量初始化
            userFeatureVectorDict[record[0]] = [0 for i in range(23)]
        userFeatureVectorDict[record[0]][courseTypeDict[record[1]] - 1] += 1  # 记录用户在这个课程下学习了
        if typeCourseDict.get(courseTypeDict[record[1]], 0) == 0:
            typeCourseDict[courseTypeDict[record[1]]] = dict()
        if typeCourseDict[courseTypeDict[record[1]]].get(record[1], -1) == -1:
            typeCourseDict[courseTypeDict[record[1]]][record[1]] = 0
        typeCourseDict[courseTypeDict[record[1]]][record[1]] += 1
    for t in typeCourseDict.keys():
        tSum = sum(typeCourseDict[t].values())
        for c in typeCourseDict[t].keys():
            typeCourseDict[t][c] = typeCourseDict[t][c]/tSum


def trainWithCluster(trainSet, estimator):
    curUser = -1
    curUserType = -1
    for record in trainSet:
        if record[0] != curUser:
            curUser = record[0]
            curUserType = estimator.predict([userFeatureVectorDict[record[0]]])[0]
        if clusterTypeDict.get(curUserType, 0) == 0:
            clusterTypeDict[curUserType] = [0 for i in range(23)]
        clusterTypeDict[curUserType][courseTypeDict[record[1]] - 1] += 1
    for t in clusterTypeDict.keys():
        t_sum = sum(clusterTypeDict[t])
        clusterTypeDict[t] = [clusterTypeDict[t][i]/t_sum for i in range(len(clusterTypeDict[t]))]


def score(typePercent, cid):
    if typeCourseDict[courseTypeDict[cid]].get(cid, 0) == 0:
        return 0
    return typePercent * typeCourseDict[courseTypeDict[cid]][cid]


def recommendForUser(uid, N):
    userCourseList = []
    for c in courseTypeDict.keys():
        s = 0
        if userFeatureVectorDict[uid][courseTypeDict[c] - 1] > 0:
            s = score(userFeatureVectorDict[uid][courseTypeDict[c] - 1], c)
        userCourseList.append((c, s))
    userCourseList.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in userCourseList[:N]]


def recommendForUserWithCluster(userType, N):
    if clusterRecDict.get(userType, 0) == 0:
        userTypeCourseList = []
        for c in courseTypeDict.keys():
            s = 0
            if clusterTypeDict.get(userType, 0) == 0:
                clusterTypeDict[userType] = [0 for i in range(23)]
            if clusterTypeDict[userType][courseTypeDict[c] - 1] > 0:
                s = score(clusterTypeDict[userType][courseTypeDict[c] - 1], c)
            userTypeCourseList.append((c, s))
        userTypeCourseList.sort(key=lambda x: x[1], reverse=True)
        clusterRecDict[userType] = userTypeCourseList
    return [x[0] for x in clusterRecDict[userType][:N]]


def getSingleAccuracyAndRecall(userTabList, recommendList):
    tabTimes = 0
    notRecall = 0
    for c in userTabList:
        if c in recommendList:
            tabTimes += 1
        else:
            notRecall += 1
    return tabTimes/len(recommendList), 1 - (notRecall/len(userTabList))


def test(testSet, N):
    """
    :param testSet: 测试集
    :param N: 要推荐多少个
    :return: 精度 和 召回率
    """
    curUser = 0
    tabList = []
    accuracyList = []
    recallList = []
    for en in testSet:
        if en[0] != curUser:
            cur_acc, cur_recall = getSingleAccuracyAndRecall(tabList, recommendForUser(curUser, N))
            accuracyList.append(cur_acc)
            recallList.append(cur_recall)
            curUser = en[0]
            tabList = [en[1]]
        else:
            tabList.append(en[1])
    cur_acc, cur_recall = getSingleAccuracyAndRecall(tabList, recommendForUser(curUser, N))
    accuracyList.append(cur_acc)
    recallList.append(cur_recall)
    print('N: {0}, accuracy: {1}; recall: {2}'.format(N, sum(accuracyList)/len(accuracyList), sum(recallList)/len(recallList)))
    return sum(accuracyList)/len(accuracyList), sum(recallList)/len(recallList)


def testWithCluster(testSet, N, estimator):
    curUser = 0
    curType = estimator.predict([userFeatureVectorDict[curUser]])[0]
    tabList = []
    accuracyList = []
    recallList = []
    for en in testSet:
        if en[0] != curUser:
            cur_acc, cur_recall = getSingleAccuracyAndRecall(tabList, recommendForUserWithCluster(curType, N))
            accuracyList.append(cur_acc)
            recallList.append(cur_recall)
            curUser = en[0]
            curType = estimator.predict([userFeatureVectorDict[curUser]])[0]
            tabList = [en[1]]
        else:
            tabList.append(en[1])
    cur_acc, cur_recall = getSingleAccuracyAndRecall(tabList, recommendForUserWithCluster(curType, N))
    accuracyList.append(cur_acc)
    recallList.append(cur_recall)
    print('N: {0}, accuracy: {1}; recall: {2}'.format(N, sum(accuracyList)/len(accuracyList), sum(recallList)/len(recallList)))
    return sum(accuracyList)/len(accuracyList), sum(recallList)/len(recallList)


def testWithAutoRec(testSet, N, autoRecModel, itemsNum=1302):
    def tab2rating(tabs):
        return [5 if t in tabs else 0 for t in range(itemsNum)]
    curUser = 0
    tabList = []
    accuracyList = []
    recallList = []
    for en in testSet:
        if en[0] != curUser:
            cur_acc, cur_recall = getSingleAccuracyAndRecall(tabList, list(autoRecModel.recommend_user(np.array(tab2rating(tabList)), N)))
            accuracyList.append(cur_acc)
            recallList.append(cur_recall)
            curUser = en[0]
            tabList = [en[1]]
        else:
            tabList.append(en[1])
    cur_acc, cur_recall = getSingleAccuracyAndRecall(tabList, list(autoRecModel.recommend_user(np.array(tab2rating(tabList)), N)))
    accuracyList.append(cur_acc)
    recallList.append(cur_recall)
    print('N: {0}, accuracy: {1}; recall: {2}'.format(N, sum(accuracyList)/len(accuracyList), sum(recallList)/len(recallList)))
    return sum(accuracyList)/len(accuracyList), sum(recallList)/len(recallList)


if __name__ == '__main__':
    trainEnrollments, testEnrollments = getTrainTest()
    kMeansEstimator = getKMeansEstimator()  # 默认聚类对象
    courseTypeDict = loadCourseTypeDict()  # 课程类型字典，key为课程编号，value为课程类型
    userFeatureVectorDict = dict()  # 用户特征向量字典，key为用户编号，value为用户特征向量
    typeCourseDict = dict()  # 类型课程字典，key为类型编号，value为该类型下的所有课程
    clusterTypeDict = dict()  # 用户聚类之后，记录各个用户类别观看课程类型的类别字典
    clusterRecDict = dict()  # 聚类推荐结果字典，key为用户类别编号，value为这个类别的推荐结果
    train(trainEnrollments)
    # 假装test
    barWidth = 0.5
    NList = [5, 10, 20, 50, 100]
    colorList = ['r', 'orange', 'pink', 'g', 'b', 'purple']
    X = ['single user', 'clusters 20', 'AutoRec', 'itemCF']
    topAccuracyList = dict()
    topRecallList = dict()
    f = open('result/result.txt', 'w+')
    print('Single user:')
    f.write('Single user:\n')
    for n in NList:
        if topAccuracyList.get(n, 0) == 0:
            topAccuracyList[n] = []
            topRecallList[n] = []
        curAcc, curRecall = test(testEnrollments, n)
        topAccuracyList[n].append(curAcc * 100)
        topRecallList[n].append(curRecall * 100)
        f.write('N: {0}, accuracy: {1}; recall: {2}\n'.format(n, curAcc, curRecall))
    print('----------')
    f.write('----------\n')
    # for i in range(10, 27, 2):
    i = 20
    f.write('cluster k = {0}:\n'.format(i))
    print('cluster k = {0}:'.format(i))
    kMeansEstimator = getKMeansEstimator(n_clusters=i, init='k-means++')
    clusterTypeDict = dict()
    clusterRecDict = dict()
    trainWithCluster(trainEnrollments, kMeansEstimator)
    for n in NList:
        curAcc, curRecall = testWithCluster(testEnrollments, n, kMeansEstimator)
        topAccuracyList[n].append(curAcc * 100)
        topRecallList[n].append(curRecall * 100)
        f.write('N: {0}, accuracy: {1}; recall: {2}\n'.format(n, curAcc, curRecall))
    print('----------')
    f.write('----------\n')
    print('AutoRec:')
    f.write('AutoRec:\n')
    autoRec = getAutoRecModel()
    for n in NList:
        curAcc, curRecall = testWithAutoRec(testEnrollments, n, autoRec)
        topAccuracyList[n].append(curAcc * 100)
        topRecallList[n].append(curRecall * 100)
        f.write('N: {0}, accuracy: {1}; recall: {2}\n'.format(n, curAcc, curRecall))
    print('----------')
    f.write('----------\n')
    itemCF = itemBasedCF(trainSet=trainEnrollments, testSet=testEnrollments)
    item_k = 20
    print('itemCF:')
    f.write('itemCF:\n')
    for n in NList:
        curAcc, curRecall = itemCF.test(k=item_k, N=n)
        topAccuracyList[n].append(curAcc * 100)
        topRecallList[n].append(curRecall * 100)
        print('N: {0}, accuracy: {1}; recall: {2}'.format(n, curAcc, curRecall))
        f.write('N: {0}, accuracy: {1}; recall: {2}\n'.format(n, curAcc, curRecall))
    f.close()
    for i in NList:
        plt.bar(X, topAccuracyList[i], width=barWidth, color=colorList)
        plt.xlabel('Numbers of K in K Means')
        plt.ylabel('Accuracy(%)')
        plt.title('Accuracy of top {0}'.format(i))
        plt.show()
        plt.savefig('result/Accuracy_Top_{0}.jpg'.format(i))
    for i in NList:
        plt.bar(X, topRecallList[i], width=barWidth, color=colorList)
        plt.xlabel('Method')
        plt.ylabel('Recall(%)')
        plt.title('Recall of top {0}'.format(i))
        plt.show()
        plt.savefig('result/Recall_Top_{0}.jpg'.format(i))