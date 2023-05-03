import os
import time
import numpy as np
import pandas as pd
import csv
import math
import random
from sklearn.model_selection import KFold,StratifiedKFold
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import StratifiedKFold
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from scipy import interp
from itertools import cycle
from sklearn.model_selection import KFold,LeaveOneOut,LeavePOut,ShuffleSplit
from sklearn.metrics import precision_recall_curve

# 定义函数
def ReadMyCsv(SaveList, fileName):
    csv_reader = csv.reader(open(fileName))
    for row in csv_reader:  # 把每个rna疾病对加入OriginalData，注意表头
        for i in range(len(row)):
            row[i] = float(row[i])
        SaveList.append(row)
    return

def storFile(data, fileName):
    with open(fileName, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    return

def MyEnlarge(x0, y0, width, height, x1, y1, times, mean_fpr, mean_tpr, thickness=1, color = 'blue'):
    def MyFrame(x0, y0, width, height):
        import matplotlib.pyplot as plt
        import numpy as np

        x1 = np.linspace(x0, x0, num=20)  # 生成列的横坐标，横坐标都是x0，纵坐标变化
        y1 = np.linspace(y0, y0, num=20)
        xk = np.linspace(x0, x0 + width, num=20)
        yk = np.linspace(y0, y0 + height, num=20)

        xkn = []
        ykn = []
        counter = 0
        while counter < 20:
            xkn.append(x1[counter] + width)
            ykn.append(y1[counter] + height)
            counter = counter + 1

        plt.plot(x1, yk, color='k', linestyle=':', lw=1, alpha=1)  # 左
        plt.plot(xk, y1, color='k', linestyle=':', lw=1, alpha=1)  # 下
        plt.plot(xkn, yk, color='k', linestyle=':', lw=1, alpha=1)  # 右
        plt.plot(xk, ykn, color='k', linestyle=':', lw=1, alpha=1)  # 上

        return
    # 画虚线框
    width2 = times * width
    height2 = times * height
    MyFrame(x0, y0, width, height)
    MyFrame(x1, y1, width2, height2)

    # 连接两个虚线框
    xp = np.linspace(x0, x1 + width2, num=20)
    yp = np.linspace(y0, y1 + height2, num=20)
    plt.plot(xp, yp, color='k', linestyle=':', lw=1, alpha=1)

    # 小虚框内各点坐标
    XDottedLine = []
    YDottedLine = []
    counter = 0
    while counter < len(mean_fpr):
        if mean_fpr[counter] > x0 and mean_fpr[counter] < (x0 + width) and mean_tpr[counter] > y0 and mean_tpr[counter] < (y0 + height):
            XDottedLine.append(mean_fpr[counter])
            YDottedLine.append(mean_tpr[counter])
        counter = counter + 1

    # 画虚线框内的点
    # 把小虚框内的任一点减去小虚框左下角点生成相对坐标，再乘以倍数（4）加大虚框左下角点
    counter = 0
    while counter < len(XDottedLine):
        XDottedLine[counter] = (XDottedLine[counter] - x0) * times + x1
        YDottedLine[counter] = (YDottedLine[counter] - y0) * times + y1
        counter = counter + 1


    plt.plot(XDottedLine, YDottedLine, color=color, lw=thickness, alpha=1)
    return

def MyConfusionMatrix(y_real,y_predict):
    from sklearn.metrics import confusion_matrix
    CM = confusion_matrix(y_real, y_predict)
    print(CM)
    CM = CM.tolist()
    TN = CM[0][0]
    FP = CM[0][1]
    FN = CM[1][0]
    TP = CM[1][1]
    print('TN:%d, FP:%d, FN:%d, TP:%d' % (TN, FP, FN, TP))
    Acc = (TN + TP) / (TN + TP + FN + FP)
    Sen = TP / (TP + FN)
    Spec = TN / (TN + FP)
    Prec = TP / (TP + FP)
    MCC = (TP * TN - FP * FN) / math.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))
    # 分母可能出现0，需要讨论待续
    print('Acc:', round(Acc, 4))
    print('Sen:', round(Sen, 4))
    print('Spec:', round(Spec, 4))
    print('Prec:', round(Prec, 4))
    print('MCC:', round(MCC, 4))
    Result = []
    Result.append(round(Acc, 4))
    Result.append(round(Sen, 4))
    Result.append(round(Spec, 4))
    Result.append(round(Prec, 4))
    Result.append(round(MCC, 4))
    return Result

def MyAverage(matrix):
    SumAcc = 0
    SumSen = 0
    SumSpec = 0
    SumPrec = 0
    SumMcc = 0
    counter = 0
    while counter < len(matrix):
        SumAcc = SumAcc + matrix[counter][0]
        SumSen = SumSen + matrix[counter][1]
        SumSpec = SumSpec + matrix[counter][2]
        SumPrec = SumPrec + matrix[counter][3]
        SumMcc = SumMcc + matrix[counter][4]
        counter = counter + 1
    print('AverageAcc:',SumAcc / len(matrix))
    print('AverageSen:', SumSen / len(matrix))
    print('AverageSpec:', SumSpec / len(matrix))
    print('AveragePrec:', SumPrec / len(matrix))
    print('AverageMcc:', SumMcc / len(matrix))
    return

def MyStd(result):
    import numpy as np
    NewMatrix = []
    counter = 0
    while counter < len(result[0]):
        row = []
        NewMatrix.append(row)
        counter = counter + 1
    counter = 0
    while counter < len(result):
        counter1 = 0
        while counter1 < len(result[counter]):
            NewMatrix[counter1].append(result[counter][counter1])
            counter1 = counter1 + 1
        counter = counter + 1
    StdList = []
    MeanList = []
    counter = 0
    while counter < len(NewMatrix):
        # std
        arr_std = np.std(NewMatrix[counter], ddof=1)
        StdList.append(arr_std)
        # mean
        arr_mean = np.mean(NewMatrix[counter])
        MeanList.append(arr_mean)
        counter = counter + 1
    result.append(MeanList)
    result.append(StdList)
    # 换算成百分比制
    counter = 0
    while counter < len(result):
        counter1 = 0
        while counter1 < len(result[counter]):
            result[counter][counter1] = round(result[counter][counter1] * 100, 2)
            counter1 = counter1 + 1
        counter = counter + 1
    return result
# CB91_Blue = '#2CBDFE'
# CB91_Green = '#47DBCD'
# CB91_Pink = '#F3A0F2'
# CB91_Purple = '#9D2EC5'
# CB91_Violet = '#661D98'
# CB91_Amber = '#F5B14C'
#
# CB91_red = '#FF0000'
# CB91_gray = '#808080'
# CB91_cyan = '#00FFFF'
# CB91_orange = '#FFA500'
# CB91_block = '#000000'
CB91_darkgrey = 'darkgrey'
CB91_darkorange = 'darkorange'
CB91_lightgreen = 'lightgreen'
CB91_lightsteelblue = 'lightsteelblue'
CB91_cyan = 'cyan'
CB91_mediumpurple = 'mediumpurple'
CB91_peru = 'peru'
CB91_deepskyblue = 'deepskyblue'
CB91_violet = 'violet'
CB91_slategray = 'slategray'
CB91_black = 'tomato'
tprs = []
aucs = []
mean_fpr = np.linspace(0, 1, 1000)
i = 0
colorlist = [CB91_darkgrey, CB91_darkorange, CB91_lightgreen, CB91_lightsteelblue, CB91_cyan, CB91_mediumpurple, CB91_peru, CB91_deepskyblue, CB91_violet, CB91_slategray, CB91_black]

# 用于保存混淆矩阵
AllResult = []

counter0 = 0
while counter0 < 10:
    print(i)
    # 读取文件
    RealAndPrediction = []
    RealAndPredictionProb = []
    RAPName ='save_model/10_fold/10fold_'+ str(counter0+1) + '_int.csv'
    RAPNameProb ='save_model/10_fold/10fold_'+ str(counter0+1) + '_pro.csv'
    ReadMyCsv(RealAndPrediction, RAPName)
    ReadMyCsv(RealAndPredictionProb, RAPNameProb)
    # 生成Real和Prediction
    Real = []
    Prediction = []
    PredictionProb = []
    counter = 0
    while counter < len(RealAndPrediction):
        Real.append(int(RealAndPrediction[counter][0]))
        Prediction.append(RealAndPrediction[counter][1])
        PredictionProb.append(RealAndPredictionProb[counter][1])
        counter = counter + 1

    # 画图
    fpr, tpr, thresholds = precision_recall_curve(Real,PredictionProb)
    # # 增加零点
    roc_auc = auc(tpr, fpr)
    aucs.append(roc_auc)
    fpr = fpr.tolist()
    tpr = tpr.tolist()
    #fpr.insert(0, 0)
    #tpr.insert(0, 0)
    tprs.append(interp(mean_fpr, fpr, tpr))
    #tprs[-1][0] = 0.0
    if i + 1 == 1:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dst fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    elif i + 1 == 2:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dnd fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    elif i + 1 == 3:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%drd fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    elif i + 1 == 4:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    elif i + 1 == 5:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    elif i + 1 == 6:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    elif i + 1 == 7:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    elif i + 1 == 8:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    elif i + 1 == 9:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    else:
        plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
                 label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # if i + 1 == 1:
    #     plt.plot(tpr, fpr, lw=1.5, alpha=0.8, color=colorlist[i],
    #              label='%dst fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # elif i + 1 == 2:
    #     plt.plot(tpr, fpr, lw=1.5, alpha=0.8, color=colorlist[i],
    #              label='%dnd fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # elif i + 1 == 3:
    #     plt.plot(tpr, fpr, lw=1.5, alpha=0.8, color=colorlist[i],
    #              label='%drd fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # else:
    #     plt.plot(tpr, fpr, lw=1.5, alpha=0.8, color=colorlist[i],
    #              label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # if i + 1 == 1:
    #     plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
    #              label='%dst fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # elif i + 1 == 2:
    #     plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
    #              label='%dnd fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # elif i + 1 == 3:
    #     plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
    #              label='%drd fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # else:
    #     plt.plot(fpr, tpr, lw=1.5, alpha=0.8, color=colorlist[i],
    #              label='%dth fold (AUPR = %0.4f)' % (i + 1, roc_auc))
    # plt.plot(mean_fpr, tprs[i], lw=1.5, alpha=0.8, color=colorlist[i],
    #                   label='fold %d (AUC = %0.4f)' % (i, roc_auc))
    # MyEnlarge(0.75, 0.7, 0.25, 0.25, 0, 0.01, 2, mean_fpr, tprs[i], 1.5, colorlist[i])

    # 混淆矩阵
    Result = MyConfusionMatrix(Real, Prediction)  #
    AllResult.append(Result)
    AllResult[i].append(roc_auc)

    i += 1
    counter0 = counter0 + 1


MyAverage(AllResult)
# AllResult
# print('AllResult', AllResult)
MyNew = MyStd(AllResult)

print(MyNew)#无需再次保存

# 画均值
mean_tpr = np.mean(tprs, axis=0)
#mean_tpr[-1] = 1.0
mean_auc = auc(mean_fpr, mean_tpr)
std_auc = np.std(aucs)


print('mean_fpr', mean_fpr)
print('mean_tpr', mean_tpr)
FprAndTpr = []
counter = 0
while counter < len(mean_fpr):
    pair = []
    pair.append(mean_fpr[counter])
    pair.append(mean_tpr[counter])
    FprAndTpr.append(pair)
    counter = counter + 1
# storFile(FprAndTpr, 'save_model/10_fold/10foldPR_FprAndTprRPC.csv')#这个文件是为了和别的。消融实验的模型的结果比较，用来绘制比较的PR图


plt.plot(mean_tpr, mean_fpr, color=colorlist[10],
         label=r'Average (AUPR = %0.4f)' % (mean_auc),
         lw=2, alpha=1)
# MyEnlarge(0.7, 0.7, 0.25, 0.25, 0, 0.01, 2, mean_fpr, mean_tpr, 2, colorlist[5])
plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05])
plt.xlabel('Recall',fontsize=13)
plt.ylabel('Precision',fontsize=13)
plt.title('Precision recall')
plt.legend(loc='best')

# # 保存图片
plt.savefig('PR-10fold.pdf',dpi=310)
plt.show()























