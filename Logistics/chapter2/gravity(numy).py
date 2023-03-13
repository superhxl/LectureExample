#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Bruce Han <superhxl@gmail.com>
#
# Distributed under terms of the MIT license.

"""
中心法求解单设施选址问题
"""
import numpy as np


def distance(p1, p2):
    """
    计算给定两个点p1和p2的距离
    p1,p2:点的坐标，以numpy数组形式传入，譬如:p1 = (1, 2, 3), p2 = (3, 3, 2)
    如果两个数组的长度不一致，则打印错误信息，并返回None
    """
    if p1.shape[0] != p2.shape[0]:
        # 两个点坐标维度不一致，返回空值
        print("Error, the two points should be in the same sapce.")
        return None
    else:
        # 计算各个维度上坐标的差的平方，并累加开方
        return (((p1 - p2) ** 2).sum()) ** 0.5


def gravity(initDc, customers, weights, error=0.05):
    """中心法
    dc：给定初始位置
    customers: 客户坐标列表
    weights: 客户权重列表
    error: 允许的误差
    """
    currDc = initDc
    while True:
        # dc到各个顾客的距离
        print("The current Dc is:", currDc)
        dist = np.array([distance(currDc, c) for c in customers])
        print("\tThe distance to customers is:", dist)

        sumx = (customers[:, 0] * weights / dist).sum()
        sumy = (customers[:, 1] * weights / dist).sum()
        sumw = (weights / dist).sum()

        newp = np.array((sumx / sumw, sumy / sumw))

        if distance(currDc, newp) < error:
            return newp
        else:
            # update the newp as currDc
            currDc = newp


def main():
    customer = np.array(((3, 1), (5, 2), (4, 3), (2, 4), (1, 5)))
    weight = np.array((1, 7, 3, 3, 6))
    initDc = np.array((0, 0))
    dcx, dcy = gravity(initDc, customer, weight, 0.001)
    print("The best position is", dcx, dcy)


if __name__ == "__main__":
    main()
