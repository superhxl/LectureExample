#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 Bruce Han <superhxl@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Python调用CPLEX、贪婪启发式算法求解仓库选址问题
"""
import pandas as pd
from docplex.mp.model import Model


class location_Prob:
    def __init__(self, filename="./location.csv"):
        """算例数据"""
        self.data = pd.read_csv(filename, index_col=0)

    def try_remove(self, node):
        """试移除节点node，计算成本增加"""
        new_selected = self.selected[:]
        i = self.selected.index(node)
        new_selected.pop(i)

        min_cost2 = self.data[new_selected].min(axis=1)
        return node, self.data["Demand"].mul(min_cost2 - self.min_cost).sum()

    def greedy(self, p):
        """构造初始解"""
        self.min_arg = self.data.iloc[:, :-1].idxmin(axis=1)
        self.min_cost = self.data.iloc[:, :-1].min(axis=1)
        total_Cost = (self.data["Demand"] * self.min_cost).sum()

        self.selected = list(self.min_arg.unique())
        while len(self.selected) > p:
            print("The objective is: {}".format(total_Cost))
            print("The selected nodes are:", self.selected)
            reduced_cost = map(self.try_remove, self.selected)
            d = pd.Series(dict(reduced_cost), dtype="float64")
            total_Cost += d.min()
            print(
                "\tNode {} is removed, and cost raised to {}".format(
                    d.idxmin(), total_Cost
                )
            )
            self.selected = list(d.drop(d.idxmin()).index)
            self.min_arg = self.data[self.selected].idxmin(axis=1)
            self.min_cost = self.data[self.selected].min(axis=1)

        print("The objective is: {}".format(total_Cost))
        print("The selected nodes are:", self.selected)
        print("The assignment is:")
        print(self.min_arg)

    def optimize(self, p):
        prob = Model("location")

        # 定义决策变量
        customers = list(self.data.index)
        nodes = list(self.data.columns)[:-1]

        x = prob.binary_var_dict(keys=nodes, name="x")
        y = prob.binary_var_matrix(keys1=customers, keys2=nodes, name="y")
        # 目标函数
        prob.minimize(
            prob.sum(
                y[(i, j)] * self.data.loc[i, j] * self.data.loc[i, "Demand"]
                for i in customers
                for j in nodes
            )
        )

        # 约束条件
        # 需求被满足
        prob.add_constraints(
            [prob.sum(y[(i, j)] for j in nodes) == 1 for i in customers],
            names=["Demand_%s" % c for c in customers],
        )

        # 一致性约束
        prob.add_constraints(
            [y[(i, j)] - x[j] <= 0 for i in customers for j in nodes],
            names=["Cons_%s_%s" % (i, j) for i in customers for j in nodes],
        )

        # 数目限制
        prob.add_constraint(prob.sum(x[j] for j in nodes) == p, "numConst")

        # 导出模型
        prob.export_as_lp("location.lp")

        # 模型求解
        sol = prob.solve()
        if sol:
            print("The optimal objective is:%6.3f" % sol.objective_value)
            selected = [j for j in nodes if sol[x[j]]]
            print("Selected nodes are:", selected)
            assignment = [(i, j) for i in customers for j in nodes if sol[y[(i, j)]]]
            print("Assignment is:\n", assignment)


def main():
    prob = location_Prob()
    print(prob.data)
    prob.greedy(2)

    prob.optimize(2)


if __name__ == "__main__":
    main()
