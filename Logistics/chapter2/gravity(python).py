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


def distance(p1, p2):
    """
    计算给定两个点p1和p2的距离
    p1,p2:点的坐标，以元组形式传入，譬如:p1 = (1, 2, 3), p2 = (3, 3, 2)
    如果两个元组的长度不一致，则打印错误信息，并返回None
    """
    if len(p1) != len(p2):
        # 两个点坐标维度不一致，返回空值
        print("Error, the two points should be in the same sapce.")
        return None
    else:
        sum = 0
        # 计算各个维度上坐标的差的平方，并累加到sum
        for i in range(len(p1)):
            sum += (p1[i] - p2[i]) ** 2

        return sum ** 0.5


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
        dist = [distance(currDc, c) for c in customers]
        print("\tThe distance to customers is:", dist)

        sumx, sumy, sumw = 0, 0, 0
        for (c, w, d) in zip(customers, weights, dist):
            sumx += c[0] * w / d
            sumy += c[1] * w / d
            sumw += w / d

        newp = (sumx / sumw, sumy / sumw)

        if distance(currDc, newp) < error:
            return newp
        else:
            # update the newp as currDc
            currDc = newp


def main():
    customer = ((3, 1), (5, 2), (4, 3), (2, 4), (1, 5))
    weight = (1, 7, 3, 3, 6)

    dcx, dcy = gravity((0, 0), customer, weight, 0.001)
    print("The best position is", dcx, dcy)


if __name__ == "__main__":
    main()
