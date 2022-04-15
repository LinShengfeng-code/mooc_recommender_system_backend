# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 训练AutoRec模型 }
# @Date: 2022/2/26 3:27 下午
import os

from rec.AutoRec.DataProcessing import *
from rec.AutoRec.AutoRec import *
from rec.AutoRec.Trainer import Trainer

autorec_config = {
    'train_ratio': 0.9,
    'num_epoch': 200,
    'batch_size': 100,
    'optimizer': 'adam',
    'adam_lr': 1e-3,
    'l2_regularization': 1e-4,
    'num_users': 82535,
    'num_items': 1302,
    'hidden_units': 500,
    'lambda': 1,
    'device_id': 2,
    'use_cuda': False,
    'data_file': 'Data/mooc.train.rating.transfer',
    'model_name': 'Models/AutoRecMOOC.model'
}


def getAutoRecModel():
    autorec_config['model_name'] = '/Users/linshengfeng/学习/大四上/毕业设计/mooc_recommender_system/mooc_back_end/rec/Models/AutoRecMOOC.model'
    autoRecModel = AutoRec(config=autorec_config)
    autoRecModel.loadModel(map_location=torch.device('cpu'))
    return autoRecModel


if __name__ == '__main__':
    # AutoRec 自编码器协同过滤算法
    train_r, train_mask_r, test_r, test_mask_r, \
    user_train_set, item_train_set, user_test_set, item_test_set = \
       dataProcess(autorec_config['data_file'], autorec_config['num_users'], autorec_config['num_items'],
                   autorec_config['train_ratio'])
    # 实例化AutoRec对象
    autorec = AutoRec(config=autorec_config)
    # 模型训练阶段
    # 实例化模型训练器
    trainer = Trainer(model=autorec, config=autorec_config)
    # 开始训练
    trainer.train(train_r, train_mask_r)
    # 保存模型
    trainer.save()

    # 模型测试阶段
    autorec.loadModel(map_location=torch.device('cpu'))

    # 从测试集中随便抽取几个用户，推荐5个商品
    print("用户1推荐列表: ", autorec.recommend_user(test_r[0], 10))
    print("用户2推荐列表: ", autorec.recommend_user(test_r[79], 10))
    print("用户3推荐列表: ", autorec.recommend_user(test_r[12345], 10))

    autorec.evaluate(test_r, test_mask_r, user_test_set=user_test_set, user_train_set=user_train_set,
                     item_test_set=item_test_set, item_train_set=item_train_set)
