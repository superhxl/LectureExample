#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 Bruce Han superhxl@gmail.com
#
# Distributed under terms of the MIT license.

"""
求解鲍摩-瓦尔夫模型
"""
import numpy as np
import pandas as pd
from docplex.mp.model import Model


class Baumol:
    def __init__(self, filename="baumoul.xlsx", theta=0.8):

        self.theta = theta
        # 工厂到配送中心的距离，以及工厂的供应量
        self.df1 = pd.read_excel(filename, "data1", index_col=0)

        # 配送中心到用户，以及用户的需求量Demand
        self.df2 = pd.read_excel(filename, "data2", index_col=0)

        # 各配送中心的转运量
        self.vol = pd.Series(data=0, index=self.df1.columns[:-1])

        # 工厂到用户的最短距离
        self.shippingCost = pd.DataFrame(
            index=self.df1.index, columns=self.df2.columns[:-1]
        )
        # 工程到用户的最短距离所经过的配送中心
        self.dcUsed = pd.DataFrame(index=self.df1.index, columns=self.df2.columns[:-1])

    def cal_shippingcost(self):
        """计算运输成本"""

        for f in self.df1.index:
            for c in self.df2.columns[:-1]:
                arr = np.array(
                    [
                        self.df1.loc[f, d]
                        + self.df2.loc[d, c]
                        + self.df2.loc[d, "VC"]
                        * self.theta
                        * (self.vol[d]) ** self.theta
                        for d in self.df1.columns[:-1]
                    ]
                )
                self.shippingCost.loc[f, c] = arr.min()
                self.dcUsed.loc[f, c] = self.df1.columns[arr.argmin()]

    def create_transport_model(self):
        """建立运输模型"""
        model = Model("trans")

        # 定义决策变量
        self.varx = model.continuous_var_matrix(
            keys1=self.shippingCost.index, keys2=self.shippingCost.columns, name="x"
        )

        # 目标函数
        model.minimize(
            model.sum(
                self.shippingCost.loc[factory, customer]
                * self.varx[(factory, customer)]
                for factory in self.shippingCost.index
                for customer in self.shippingCost.columns
            )
        )

        # 约束条件：需求约束
        for customer in self.shippingCost.columns:
            model.add_constraint(
                model.sum(
                    self.varx[(factory, customer)]
                    for factory in self.shippingCost.index
                )
                == self.df2.loc["Demand", customer],
                ctname="Demand%s" % customer,
            )

        # 约束条件：供给约束
        for factory in self.shippingCost.index:
            model.add_constraint(
                model.sum(
                    self.varx[(factory, customer)]
                    for customer in self.shippingCost.columns
                )
                <= self.df1.loc[factory, "Supply"],
                ctname="Supply_%s" % factory,
            )

        # 导出模型
        model.export_as_lp("transport.lp")

        self.model = model

    def update_model(self):
        """使用最短运输距离更新模型"""
        sol = self.model.solve()
        if sol:
            print("The optimal objective is: {}".format(sol.objective_value))
            # 计算各配送中心转运量
            for factory in self.shippingCost.index:
                for customer in self.shippingCost.columns:
                    if abs(sol[self.varx[(factory, customer)]]) > 1e-6:
                        cur_dc = self.dcUsed.loc[factory, customer]
                        self.vol[cur_dc] += sol[self.varx[(factory, customer)]]

            print(self.vol)

    def iterate(self):
        """迭代计算"""
        pass


def main():
    b1 = Baumol()
    print(b1.df1)
    print(b1.df2)
    b1.cal_shippingcost()
    b1.create_transport_model()

    b1.update_model()


if __name__ == "__main__":
    main()
