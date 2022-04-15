# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 处理数据的模块 }
# @Date: 2022/2/26 11:43 上午
import torch
import numpy as np
import torch.utils.data as Data


def dataTransform(old_filename, new_filename):
    """
    在不破坏原有数据集的情况下，产生一个五分制的新数据集
    :param old_filename: 老文件名， 读取的文件
    :param new_filename:  新文件名，要转记的目标文件
    :return: None
    """
    with open(old_filename, 'r') as f:
        lines = f.readlines()
    with open(new_filename, 'w') as ff:
        for i in range(len(lines)):
            line = lines[i].strip().split('\t')
            new_line = line[0] + '::' + line[1] + '::5\n'
            ff.write(new_line)


def dataProcess(filename, num_users, num_items, train_ratio):
    """
    分割出训练集和测试集
    :param filename: 原数据集
    :param num_users: 用户总数
    :param num_items: 物品总数
    :param train_ratio: 训练数据比例
    :return:
    """
    fp = open(filename, 'r')
    lines = fp.readlines()

    num_total_ratings = len(lines)

    user_train_set = set()
    user_test_set = set()
    item_train_set = set()
    item_test_set = set()

    train_r = np.zeros((num_users, num_items))
    test_r = np.zeros((num_users, num_items))

    train_mask_r = np.zeros((num_users, num_items))
    test_mask_r = np.zeros((num_users, num_items))

    # 在 0 到 num_total_ratings (不含) 之间生成一个随机序列
    random_perm_idx = np.random.permutation(num_total_ratings)
    # 将数据分为训练集和测试集
    train_idx = random_perm_idx[0: int(num_total_ratings * train_ratio)]
    test_idx = random_perm_idx[int(num_total_ratings * train_ratio):]

    # 训练
    for itr in train_idx:
        line = lines[itr]
        user, item, rating = line.split("::")  # 原始数据格式：user_id::item_id::rating\n
        user_idx = int(user)  # 用户编号是从0开始的
        item_idx = int(item)  # 物品编号也是从0开始的
        train_r[user_idx][item_idx] = int(rating)
        train_mask_r[user_idx][item_idx] = 1

        user_train_set.add(user_idx)
        item_train_set.add(item_idx)

    # 测试
    for itr in test_idx:
        line = lines[itr]
        user, item, rating = line.split("::")  # 原始数据格式：user_id::item_id::rating\n
        user_idx = int(user)  # 用户编号是从0开始的
        item_idx = int(item)  # 物品编号也是从0开始的
        test_r[user_idx][item_idx] = int(rating)
        test_mask_r[user_idx][item_idx] = 1

        user_test_set.add(user_idx)
        item_test_set.add(item_idx)

    return train_r, train_mask_r, test_r, test_mask_r, user_train_set, item_train_set, user_test_set, item_test_set


def Construct_DataLoader(train_r, train_mask_r, batch_size):
    torch_dataset = Data.TensorDataset(torch.from_numpy(train_r), torch.from_numpy(train_mask_r))
    return Data.DataLoader(dataset=torch_dataset, batch_size=batch_size, shuffle=True)
