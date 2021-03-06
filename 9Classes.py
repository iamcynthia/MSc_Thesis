import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

from scipy.signal import butter,filtfilt, freqz ## for butterworth filter

## for feature extraction
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

## for training
from sklearn.model_selection import cross_val_score, cross_val_predict, KFold, StratifiedKFold

## for classifier
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB 

## for evaluation
from sklearn import metrics
from sklearn.metrics import accuracy_score, confusion_matrix , recall_score

## for under-sampling
!pip install imbalanced-learn
from imblearn.under_sampling import RandomUnderSampler
from collections import Counter
from imblearn.pipeline import make_pipeline
from imblearn.under_sampling import TomekLinks
from imblearn.over_sampling import RandomOverSampler
from imblearn.combine import SMOTETomek
from imblearn.under_sampling import EditedNearestNeighbours
from imblearn.under_sampling import OneSidedSelection

################### 1. import segmented dataset ###################
class9 = pd.read_csv('dataset.csv')
## change the labels 
for i in range(len(class9)):
  if class9.Class[i] == 'stand and get in car':
    class9.Class[i] = "stand and bend"
  elif class9.Class[i] == 'stumble':
    class9.Class[i] = "walking"
  elif class9.Class[i] == 'fall forward':
    class9.Class[i] = "fall"
  elif class9.Class[i] == 'fall backward':
    class9.Class[i] = "fall"
  elif class9.Class[i] == 'lateral fall':
    class9.Class[i] = "fall"

## find NaN rows
class9[class9.isnull().any(axis = 1)]
## fill NaN
class9.stdX = class9.stdX.fillna(0)
class9.stdY = class9.stdY.fillna(0)
class9.stdZ = class9.stdZ.fillna(0)

print("Number of Cases in Each Class - 9 Classes")
print("-----------------------------------------")
class9.Class.value_counts()


################### 2. Feature Extraction ###################
## PCA 4 dim ; LDA 3 dim
X = class9.iloc[:,:-1]
X = StandardScaler().fit_transform(X)
y = class9.iloc[:,-1]
print(X.shape)
print(np.mean(X),np.std(X))

## PCA from 12 dimension to 4 dimension
pca_4 = PCA(n_components=4)
principalComponents_4 = pca_4.fit_transform(X)
principal_4_Df = pd.DataFrame(data = principalComponents_4, columns = ['PC1', 'PC2', 'PC3', 'PC4'])  
print('Explained variation per principal component: {}'.format(pca_4.explained_variance_ratio_))  
print('PC1 holds 34.07% of the information, PC2 holds 20.6%, PC3 holds 16.9%, PC4 holds 13.2%, around 14.6% of information is lost')
principal_4_Df['Class'] = class9['Class']
principal_4_Df.head()

## LDA from 12 dim to 3
lda = LinearDiscriminantAnalysis(n_components = 3)
lda = lda.fit_transform(X,y)
LDA_3_df = pd.DataFrame(data = lda, columns=['LDA1', 'LDA2', 'LDA3'])
LDA_3_df['Class'] = class9['Class']
LDA_3_df.head()


################### 3. Model Selection ###################

################ Requirements ################
## Calculate Specificity for each trial
def Specificity():
  FP = []
  TN = []
  a = confusion_matrix(y_test,y_pred)
  for i in range(len(np.unique(y))):
    FP.append(np.sum(a[:,i]) - a[i,i])
    TN.append(np.sum(a) - np.sum(a[:,i]) - np.sum(a[i,:]) + a[i,i])
  FP = np.array(FP)
  TN = np.array(TN)
  np.set_printoptions(formatter={'float': '{:.2f}'.format})
  return TN/(FP+TN)
##############################################

################### 3. Model Selection: KNN ###################
kf = KFold(n_splits=10, shuffle=True, random_state=0)
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)

X = np.array(principal_4_Df.iloc[:,:-1])
y = np.array(principal_4_Df.iloc[:,-1])

PCA4_kf = []
PCA4_skf = []
for i in range(3,14):
  model = KNeighborsClassifier(n_neighbors=i)
  PCA4_kf.append(cross_val_score(model, X, y, cv=kf).mean())
  PCA4_skf.append(cross_val_score(model, X, y, cv=skf).mean())


X = np.array(LDA_3_df.iloc[:,:-1])
y = np.array(LDA_3_df.iloc[:,-1])

LDA3_kf = []
LDA3_skf = []
for i in range(3,14):
  model = KNeighborsClassifier(n_neighbors=i)
  LDA3_kf.append(cross_val_score(model, X, y, cv=kf).mean())
  LDA3_skf.append(cross_val_score(model, X, y, cv=skf).mean()) 


knnTable = pd.DataFrame(zip(PCA4_kf, PCA4_skf, LDA3_kf, LDA3_skf), index = ['k = 3', 'k = 4', 'k = 5', 'k = 6', 'k = 7', 'k = 8', 'k = 9', 'k = 10', 'k = 11', 'k = 12', 'k = 13'], columns = ['4 dim PCA kf', '4 dim PCA Skf', '3 dim LDA kf', '3 dim LDA Skf'])
knnTable = knnTable.applymap(lambda x :'%.2f%%'  %  (x*100))
print('Accuracy Score of KNN -- 9 Classes Version')
print(knnTable)


################### 3. Model Selection: Naive Bayes ###################
########## 4 dim PCA ##########
X = principal_4_Df.iloc[:,:-1]
y = principal_4_Df.iloc[:,-1]

model = GaussianNB()

# Stratified 10-Fold
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)
nbStr4 = cross_val_score(model, X, y, cv=skf)

# 10-Fold 
kf = KFold(n_splits=10)
nb4 = cross_val_score(model, X, y, cv=kf)

str4 = "{:.2%}".format(nbStr4.mean())
NB4 = "{:.2%}".format(nb4.mean())

## 3 dim LDA
X = LDA_3_df.iloc[:,:-1]
y = LDA_3_df.iloc[:,-1]

model = GaussianNB()

# Stratified 10-Fold
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)
nbStr3 = cross_val_score(model, X, y, cv=skf)

# 10-Fold 
kf = KFold(n_splits=10)
nb3 = cross_val_score(model, X, y, cv=kf)

str3 = "{:.2%}".format(nbStr3.mean())
NB3 = "{:.2%}".format(nb3.mean())

nbTable = pd.DataFrame({'Stratified CV' : [str4, str3], '10-fold CV' : [NB4, NB3]}, index=['4 dim PCA', '3 dim LDA'])
print('Accuracy Score of Naive Bayes --9 Classes Version')
print(nbTable)


################### 3. Model Selection: SVM ###################
########## 4 dim PCA ##########
X = principal_4_Df.iloc[:,:-1]
y = principal_4_Df.iloc[:,-1]

## Classifier - SVM
linear = svm.SVC(kernel='linear', C=1, decision_function_shape='ovo', probability=True).fit(X, y)
rbf = svm.SVC(kernel='rbf', gamma=1, C=1, decision_function_shape='ovo', probability=True).fit(X, y)
poly = svm.SVC(kernel='poly', degree=3, C=1, decision_function_shape='ovo', probability=True).fit(X, y)
sig = svm.SVC(kernel='sigmoid', C=1, decision_function_shape='ovo', probability=True).fit(X, y)

# Stratified 10-Fold
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state = 0)
LinearScore10 = cross_val_score(linear, X, y, cv=skf)
RbfScore10 = cross_val_score(rbf,X,y,cv=skf)
PolyScore10 = cross_val_score(poly, X, y, cv=skf)
SigScore10 = cross_val_score(sig, X, y, cv=skf)

# 10-Fold 
kf = KFold(n_splits=10, shuffle=True, random_state = 0)
LinearScore10folds = cross_val_score(linear, X, y, cv=kf)
RbfScore10folds = cross_val_score(rbf,X,y,cv=kf)
PolyScore10folds = cross_val_score(poly, X, y, cv=kf)
SigScore10folds = cross_val_score(sig, X, y, cv=kf)

# k_10_pred = cross_val_predict(SVM, X, y, cv=10)

L_skf = "{:.2%}".format(LinearScore10.mean())
R_skf = "{:.2%}".format(RbfScore10.mean())
P_skf = "{:.2%}".format(PolyScore10.mean())
S_skf = "{:.2%}".format(SigScore10.mean())
L_kf = "{:.2%}".format(LinearScore10folds.mean())
R_kf = "{:.2%}".format(RbfScore10folds.mean())
P_kf = "{:.2%}".format(PolyScore10folds.mean())
S_kf = "{:.2%}".format(SigScore10folds.mean())

########## 3 dim LDA ##########
X = LDA_3_df.iloc[:,:-1]
y = LDA_3_df.iloc[:,-1]

## Classifier - SVM
linear = svm.SVC(kernel='linear', C=1, decision_function_shape='ovo', probability=True).fit(X, y)
rbf = svm.SVC(kernel='rbf', gamma=1, C=1, decision_function_shape='ovo', probability=True).fit(X, y)
poly = svm.SVC(kernel='poly', degree=3, C=1, decision_function_shape='ovo', probability=True).fit(X, y)
sig = svm.SVC(kernel='sigmoid', C=1, decision_function_shape='ovo', probability=True).fit(X, y)

# Stratified 10-Fold
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state = 0)
LinearScore10 = cross_val_score(linear, X, y, cv=skf)
RbfScore10 = cross_val_score(rbf,X,y,cv=skf)
PolyScore10 = cross_val_score(poly, X, y, cv=skf)
SigScore10 = cross_val_score(sig, X, y, cv=skf)

# 10-Fold 
kf = KFold(n_splits=10, shuffle=True, random_state = 0)
LinearScore10folds = cross_val_score(linear, X, y, cv=kf)
RbfScore10folds = cross_val_score(rbf,X,y,cv=kf)
PolyScore10folds = cross_val_score(poly, X, y, cv=kf)
SigScore10folds = cross_val_score(sig, X, y, cv=kf)

# k_10_pred = cross_val_predict(SVM, X, y, cv=10)

L3_skf = "{:.2%}".format(LinearScore10.mean())
R3_skf = "{:.2%}".format(RbfScore10.mean())
P3_skf = "{:.2%}".format(PolyScore10.mean())
S3_skf = "{:.2%}".format(SigScore10.mean())
L3_kf = "{:.2%}".format(LinearScore10folds.mean())
R3_kf = "{:.2%}".format(RbfScore10folds.mean())
P3_kf = "{:.2%}".format(PolyScore10folds.mean())
S3_kf = "{:.2%}".format(SigScore10folds.mean())


################### 3. Model Selection: Best Classifier Results ###################
np.set_printoptions(formatter={'float': '{:.2f}'.format})
X = np.array(principal_4_Df.iloc[:,:-1])
y = np.array(principal_4_Df.iloc[:,-1])
model = KNeighborsClassifier(n_neighbors=5)
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)

overall = []
recall = np.zeros((1,9))
spe = np.zeros((1,9))
tol = np.zeros((9,9))
trial = 0
for train_index, test_index in skf.split(X,y):
  X_train, X_test = X[train_index], X[test_index]
  y_train, y_test = y[train_index], y[test_index]
  model.fit(X_train, y_train)
  y_pred = cross_val_predict(model, X_test, y_test, cv=skf)
  score = cross_val_score(model, X_test, y_test, cv=skf).mean() 
  overall.append(score)
  trial+=1
  print("KNN  k=5  4 dim PCA")
  print("Trial {}" .format(trial)) 
  print("Accuracy: {:.2%}".format(score))
  print("Sensitivity: ", recall_score(y_test, y_pred, average=None))
  print("Specificity: ", Specificity())
  # skplt.metrics.plot_confusion_matrix(y_test, y_pred, normalize=True)
  skplt.metrics.plot_confusion_matrix(y_test, y_pred, x_tick_rotation=80, figsize=(7,7))  
  spe += Specificity()
  recall += recall_score(y_test, y_pred, average=None)
  tol += confusion_matrix(y_test,y_pred)
  plt.show()
  print("---------------------------------------------------------------")

print("KNN  k=5  4 dim PCA")
print("Overall Accuracy: {:.2%} \n".format(np.mean(overall)))
print("Overall Sensitivity of each class: ")
print(recall/10)
print("\n")
print("Overall Specificity of each class: ")
print(spe/10)
print("\n")
print("Overall Confusion Matrix: ")
np.set_printoptions(formatter={'float': '{:.1f}'.format})
print(tol/10)
print("\n")
print("Number of cases in each class")
print(Counter(y))


################### 4. Under-sampling: Randomly  ###################
########## under-sample by "majority" ##########
X = np.array(principal_4_Df.iloc[:,:-1])
y = np.array(principal_4_Df.iloc[:,-1])
model = KNeighborsClassifier(n_neighbors=9)
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)
rus = RandomUnderSampler(sampling_strategy='majority', random_state=0)
pipeline = make_pipeline(rus, model)
X_res , y_res = rus.fit_resample(X, y)

overall = []
recall = np.zeros((1,9))
spe = np.zeros((1,9))
tol = np.zeros((9,9))
trial = 0
for train_index, test_index in skf.split(X,y):
  X_train, X_test = X[train_index], X[test_index]
  y_train, y_test = y[train_index], y[test_index]
  model.fit(X_train, y_train)
  y_pred = cross_val_predict(pipeline, X_test, y_test, cv=skf)
  score = cross_val_score(pipeline, X_test, y_test, cv=skf).mean() 
  overall.append(score)
  trial+=1
  print("KNN  k=5  4 dim PCA  Best Classifier under-sample by majority")
  print("Trial {}" .format(trial)) 
  print("Accuracy: {:.2%}".format(score))
  print("Sensitivity: ", recall_score(y_test, y_pred, average=None))
  print("Specificity: ", Specificity())
  # skplt.metrics.plot_confusion_matrix(y_test, y_pred, normalize=True)
  skplt.metrics.plot_confusion_matrix(y_test, y_pred, x_tick_rotation=80, figsize=(7,7))  
  spe += Specificity()
  recall += recall_score(y_test, y_pred, average=None)
  tol += confusion_matrix(y_test,y_pred)
  plt.show()
  print("---------------------------------------------------------------")

print("KNN  k=5  4 dim PCA  Best Classifier under-sample by majority")
print("Overall Accuracy: {:.2%} \n".format(np.mean(overall)))
print("Overall Sensitivity of each class: ")
print(recall/10)
print("\n")
print("Overall Specificity of each class: ")
print(spe/10)
print("\n")
print("Overall Confusion Matrix: ")
np.set_printoptions(formatter={'float': '{:.1f}'.format})
print(tol/10)
print("\n")
print("Number of cases in each class")
print(Counter(y_res))

########## under-sample by Tomek Link ##########
X = np.array(principal_4_Df.iloc[:,:-1])
y = np.array(principal_4_Df.iloc[:,-1])
model = KNeighborsClassifier(n_neighbors=9)
kf = KFold(n_splits=10, shuffle=True, random_state=0)
rus = TomekLinks(random_state=0)
pipeline = make_pipeline(rus, model)
X_res , y_res = rus.fit_resample(X, y)

overall = []
recall = np.zeros((1,9))
spe = np.zeros((1,9))
tol = np.zeros((9,9))
trial = 0
for train_index, test_index in skf.split(X,y):
  X_train, X_test = X[train_index], X[test_index]
  y_train, y_test = y[train_index], y[test_index]
  model.fit(X_train, y_train)
  y_pred = cross_val_predict(pipeline, X_test, y_test, cv=skf)
  score = cross_val_score(pipeline, X_test, y_test, cv=skf).mean() 
  overall.append(score)
  trial+=1
  print("KNN  k=5  4 dim PCA  Best Classifier under-sample by Tomek Link")
  print("Trial {}" .format(trial)) 
  print("Accuracy: {:.2%}".format(score))
  print("Sensitivity: ", recall_score(y_test, y_pred, average=None))
  print("Specificity: ", Specificity())
  # skplt.metrics.plot_confusion_matrix(y_test, y_pred, normalize=True)
  skplt.metrics.plot_confusion_matrix(y_test, y_pred, x_tick_rotation=80, figsize=(7,7))  
  spe += Specificity()
  recall += recall_score(y_test, y_pred, average=None)
  tol += confusion_matrix(y_test,y_pred)
  plt.show()
  print("---------------------------------------------------------------")

print("KNN  k=5  4 dim PCA  Best Classifier under-sample by Tomek Link")
print("Overall Accuracy: {:.2%} \n".format(np.mean(overall)))
print("Overall Sensitivity of each class: ")
print(recall/10)
print("\n")
print("Overall Specificity of each class: ")
print(spe/10)
print("\n")
print("Overall Confusion Matrix: ")
np.set_printoptions(formatter={'float': '{:.1f}'.format})
print(tol/10)
print("\n")
print("Number of cases in each class")
print(Counter(y_res))

########## under-sample by Edited Nearest Neighbours ##########
X = np.array(principal_4_Df.iloc[:,:-1])
y = np.array(principal_4_Df.iloc[:,-1])
model = KNeighborsClassifier(n_neighbors=9)
kf = KFold(n_splits=10, shuffle=True, random_state=0)
rus = EditedNearestNeighbours(random_state=0)
pipeline = make_pipeline(rus, model)
X_res , y_res = rus.fit_resample(X, y)

overall = []
recall = np.zeros((1,9))
spe = np.zeros((1,9))
tol = np.zeros((9,9))
trial = 0
for train_index, test_index in skf.split(X,y):
  X_train, X_test = X[train_index], X[test_index]
  y_train, y_test = y[train_index], y[test_index]
  model.fit(X_train, y_train)
  y_pred = cross_val_predict(pipeline, X_test, y_test, cv=skf)
  score = cross_val_score(pipeline, X_test, y_test, cv=skf).mean() 
  overall.append(score)
  trial+=1
  print("KNN  k=5  4 dim PCA  Best Classifier under-sample by Edited Nearest Neighbours")
  print("Trial {}" .format(trial)) 
  print("Accuracy: {:.2%}".format(score))
  print("Sensitivity: ", recall_score(y_test, y_pred, average=None))
  print("Specificity: ", Specificity())
  # skplt.metrics.plot_confusion_matrix(y_test, y_pred, normalize=True)
  skplt.metrics.plot_confusion_matrix(y_test, y_pred, x_tick_rotation=80, figsize=(7,7))  
  spe += Specificity()
  recall += recall_score(y_test, y_pred, average=None)
  tol += confusion_matrix(y_test,y_pred)
  plt.show()
  print("---------------------------------------------------------------")

print("KNN  k=5  4 dim PCA  Best Classifier under-sample by Edited Nearest Neighbours")
print("Overall Accuracy: {:.2%} \n".format(np.mean(overall)))
print("Overall Sensitivity of each class: ")
print(recall/10)
print("\n")
print("Overall Specificity of each class: ")
print(spe/10)
print("\n")
print("Overall Confusion Matrix: ")
np.set_printoptions(formatter={'float': '{:.1f}'.format})
print(tol/10)
print("\n")
print("Number of cases in each class")
print(Counter(y_res))

########## under-sample by SMOTE + Tomek ##########
X = np.array(principal_4_Df.iloc[:,:-1])
y = np.array(principal_4_Df.iloc[:,-1])
model = KNeighborsClassifier(n_neighbors=9)
kf = KFold(n_splits=10, shuffle=True, random_state=0)
rus = SMOTETomek(tomek=TomekLinks(sampling_strategy='majority'), random_state=0)
pipeline = make_pipeline(rus, model)
X_res , y_res = rus.fit_resample(X, y)

overall = []
recall = np.zeros((1,9))
spe = np.zeros((1,9))
tol = np.zeros((9,9))
trial = 0
for train_index, test_index in skf.split(X,y):
  X_train, X_test = X[train_index], X[test_index]
  y_train, y_test = y[train_index], y[test_index]
  model.fit(X_train, y_train)
  y_pred = cross_val_predict(pipeline, X_test, y_test, cv=skf)
  score = cross_val_score(pipeline, X_test, y_test, cv=skf).mean() 
  overall.append(score)
  trial+=1
  print("KNN  k=5  4 dim PCA  Best Classifier under-sample by SMOTE + Tomek")
  print("Trial {}" .format(trial)) 
  print("Accuracy: {:.2%}".format(score))
  print("Sensitivity: ", recall_score(y_test, y_pred, average=None))
  print("Specificity: ", Specificity())
  # skplt.metrics.plot_confusion_matrix(y_test, y_pred, normalize=True)
  skplt.metrics.plot_confusion_matrix(y_test, y_pred, x_tick_rotation=80, figsize=(7,7))  
  spe += Specificity()
  recall += recall_score(y_test, y_pred, average=None)
  tol += confusion_matrix(y_test,y_pred)
  plt.show()
  print("---------------------------------------------------------------")

print("KNN  k=5  4 dim PCA  Best Classifier under-sample by SMOTE + Tomek")
print("Overall Accuracy: {:.2%} \n".format(np.mean(overall)))
print("Overall Sensitivity of each class: ")
print(recall/10)
print("\n")
print("Overall Specificity of each class: ")
print(spe/10)
print("\n")
print("Overall Confusion Matrix: ")
np.set_printoptions(formatter={'float': '{:.1f}'.format})
print(tol/10)
print("\n")
print("Number of cases in each class")
print(Counter(y_res))


################### 4. Under-sampling: Selected Class  ###################
########## one sided selection (sampling_strategy can change)##########
np.set_printoptions(formatter={'float': '{:.2f}'.format})
X = np.array(principal_4_Df.iloc[:,:-1])
y = np.array(principal_4_Df.iloc[:,-1])
model = KNeighborsClassifier(n_neighbors=5)
kf = KFold(n_splits=10, shuffle=True, random_state=0)
us =  OneSidedSelection(n_neighbors=8, sampling_strategy=['stand and bend', 'walk up and down', 'sit and collapsed when standing', 'sit and stand', 'fall'])
pipeline = make_pipeline(us, model)
X_res , y_res = us.fit_resample(X, y)

overall = []
recall = np.zeros((1,9))
spe = np.zeros((1,9))
tol = np.zeros((9,9))
trial = 0
for train_index, test_index in kf.split(X):
  X_train, X_test = X[train_index], X[test_index]
  y_train, y_test = y[train_index], y[test_index]
  model.fit(X_train, y_train)
  y_pred = cross_val_predict(pipeline, X_test, y_test, cv=kf)
  score = cross_val_score(pipeline, X_test, y_test, cv=kf).mean() 
  overall.append(score)
  trial+=1
  print("KNN  k=5  4 dim PCA  Best Classifier under-sample by One Sided Selection")
  print("Resampled classes: \n stand and bend, walk up and down, sit and collaped when standing, \n sit and stand, fall")
  print("Trial {}" .format(trial)) 
  print("Accuracy: {:.2%}".format(score))
  print("Sensitivity: ", recall_score(y_test, y_pred, average=None))
  print("Specificity: ", Specificity())
  # skplt.metrics.plot_confusion_matrix(y_test, y_pred, normalize=True)
  skplt.metrics.plot_confusion_matrix(y_test, y_pred, x_tick_rotation=80, figsize=(7,7))
  spe += Specificity()
  recall += recall_score(y_test, y_pred, average=None)
  tol += confusion_matrix(y_test,y_pred)
  plt.show()
  print("--------------------------------------------------------------------------------")

print("KNN  k=5  4 dim PCA  Best Classifier under-sample by One Sided Selection")
print("Resampled classes: \n stand and bend, walk up and down, sit and collaped when standing, sit and stand, fall")
print("Overall Accuracy: {:.2%} \n".format(np.mean(overall)))
print("Overall Sensitivity of each class: ")
print(recall/10)
print("\n")
print("Overall Specificity of each class: ")
print(spe/10)
print("\n")
print("Overall Confusion Matrix: ")
np.set_printoptions(formatter={'float': '{:.1f}'.format})
print(tol/10)
print("\n")
print("Number of cases in each class")
print(Counter(y_res))








