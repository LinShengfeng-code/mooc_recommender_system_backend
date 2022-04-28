# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: {物品协同过滤}
# @Date: 2022/4/10 22:56
import math
import random


class itemBasedCF:
    def __init__(self, trainSet, testSet):
        self.coTable = dict()  # 物品共现矩阵/表，采用字典的哈希表形式避免稀疏矩阵
        self.similarityTable = dict()  # 物品相似度矩阵/表，同上
        self.userTabDict = dict()  # 用户点击字典，也就是保存每个用户各自注册的课程的集合
        self.trainSet = trainSet
        self.testSet = testSet
        self.testUserTabDict = dict()
        self.testUserRecDict = dict()
        self.train()

    def getItemTabTimes(self, item):
        """
        计算一个物品被总共点击的次数
        :param item: 物品编号
        :return: 一个物品被总共点击的次数
        """
        itemTabTimes = 0
        for i in list(self.coTable[item].values()):
            itemTabTimes += i
        return itemTabTimes

    def calcSimilarity(self, itemA, itemB):
        """
        计算物品A与物品B的相似度
        :param itemA: 物品A编号
        :param itemB: 物品B编号
        :return: A与B相似度
        """
        return self.coTable[itemA][itemB] / math.sqrt(self.getItemTabTimes(itemA) * self.getItemTabTimes(itemB))

    def train(self):
        """
        # 这个方法用于构建共现矩阵和相似度矩阵，也就是训练
        :return: None
        """
        # 初始化用户点击字典
        for record in self.trainSet:
            # 初始化一个用户
            if self.userTabDict.get(record[0], 0) == 0:
                self.userTabDict[record[0]] = set()
            self.userTabDict[record[0]].add(record[1])
        # 统计共现矩阵
        for i in self.userTabDict.keys():
            courseList = list(self.userTabDict[i])
            # 枚举课程列表中的课程号
            for c in courseList:
                # 枚举课程列表中的其他课程号
                for otherCourse in courseList:
                    # 如果课程号一样就跳过，不一样则执行共现矩阵的记录
                    if c != otherCourse:
                        # 缺少字典就初始化
                        if self.coTable.get(c, 0) == 0:
                            self.coTable[c] = dict()
                        if self.coTable.get(otherCourse, 0) == 0:
                            self.coTable[otherCourse] = dict()
                        # 共现矩阵更新
                        self.coTable[c][otherCourse] = self.coTable[c].get(otherCourse, 0) + 1
                        self.coTable[otherCourse][c] = self.coTable[otherCourse].get(c, 0) + 1
        # 统计相似度矩阵
        for j in self.coTable.keys():
            # 如果物品j还没有被统计，初始化一下
            if self.similarityTable.get(j, 0) == 0:
                self.similarityTable[j] = dict()
            for k in self.coTable.keys():
                # 如果物品k还没有被统计，初始化一下
                if self.similarityTable.get(k, 0) == 0:
                    self.similarityTable[k] = dict()
                # 如果k与j有关联
                if k in self.coTable[j].keys():
                    self.similarityTable[j][k] = self.similarityTable[k][j] = self.calcSimilarity(j, k)
                # 矩阵太稀疏，如果为0就不记录了
        # 可以再归一化一下

    def recommendBasedOnItem(self, item_id, k=4):
        try:
            return dict(sorted(self.similarityTable[item_id].items(), key=lambda x: x[1], reverse=True)[0:k])
        except KeyError:
            randomList = []
            for i in range(k):
                rand = random.randint(0, 1302)
                while rand in randomList:
                    rand = random.randint(0, 1302)
                randomList.append((rand, 0))
            return dict(randomList)

    def recommend(self, user_id, k, N):
        rank = dict()
        interacted_items = list(self.userTabDict[user_id])
        # 遍历用户交互过的物品列表
        for itemId in interacted_items:
            for i, sim_ij in sorted(self.similarityTable[itemId].items(), key=lambda x: x[1], reverse=True)[0:k]:
                # 如果这个物品j已经被用户点击过了，舍弃
                if i in interacted_items:
                    continue
                rank[i] = rank.get(i, 0) + sim_ij
        # 推荐权重前N的物品
        return dict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:N])

    def test(self, k, N):
        """
        测试精度和召回率
        :param k: K 个与当前物品相似的物品
        :param N: top N 推荐
        :return: 精度 和 召回率
        """
        accuracyDict, recallDict = dict(), dict()
        for record in self.testSet:
            # 初始化用户点击列表（测试）
            if not self.testUserTabDict.get(record[0], []):
                self.testUserTabDict[record[0]] = []
            # 初始化用户推荐列表（测试）
            if not self.testUserRecDict.get(record[0], []):
                # 这里把所有物品按照评分做推荐，避免后期重复推荐耗费大量时间
                self.testUserRecDict[record[0]] = list(self.recommend(record[0], k, 1302).keys())
            # 将记录中的物品加入用户点击列表（测试）
            self.testUserTabDict[record[0]].append(record[1])

        def singleTest(uid):
            """
            获取单个用户推荐结果的精度和召回率
            :param uid: 用户id
            :return: 精度和召回率
            """
            # 推荐的N个物品
            recItems = self.testUserRecDict[uid][:N]
            # 命中的物品列表
            hitList = [i for i in recItems if i in self.testUserTabDict[uid]]
            if recItems:
                return len(hitList)/len(recItems), len(hitList)/len(self.testUserTabDict[uid])
            return 0, 0

        for record in self.testSet:
            if accuracyDict.get(record[0], 0) == 0:
                acc, recall = singleTest(record[0])
                accuracyDict[record[0]] = acc
                recallDict[record[0]] = recall
        return sum(list(accuracyDict.values()))/len(accuracyDict.keys()), sum(list(recallDict.values()))/len(recallDict.keys())
