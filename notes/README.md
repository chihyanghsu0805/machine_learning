This folder contains notes from various Machine Learning (ML) / Deep Learning (DL) courses.

Including,

-   Google Machine Learning Crash Course, https://developers.google.com/machine-learning/crash-course
-   Stanford CS229 - 2018 Fall, https://youtu.be/jGwO_UgTS7I, https://cs229.stanford.edu/syllabus-autumn2018.html
-   Coursera Deep Learning Specialization, https://www.coursera.org/specializations/deep-learning
-   Coursera Stanford Machine Learning, https://www.coursera.org/learn/machine-learning?page=2
-   Deep Learning, https://www.deeplearningbook.org/

# Overview

## Problem
ML problems can be catgorized into the following,

-   `Supervised` ML have features and labels. Depending on the labels, it can be further categorized into

    -   `Classification` with discrete labels
    -   `Regression` with continuous labels

-   `Unsupervised` ML are used to find patterns in the data. Some examples are,

    -   `Clustering`
    -   Network Analysis
    -   Market Segmentation

-   `Reinforcement Learning` (RL): RL provides an environment to learn value and policy functions.

## Data

Typically, there are two types of data, `structured` and `unstructured`. Structured data refers to data that is represented with rows as subjects and columns as features. Unstructured data refers to data that do not follow this format, such as images and audios.

To build a good solution to a ML problem, it is important to understand the data, or `exploratory data analysis (EDA)`. In EDA, it is typical to collect representative statistics (such as mean, minimum, maximum, etc) for each feature and detect outliers and errors. Histogram visualization also helps with understanding the feature distribution to determine possible means to normalize the features. After understanding the data, various approaches can be applied to the features to help with model training. For example, normalizing the features allows certain algorithms to converge faster. These approaches are referred to as `feature engineering`.

### Feature Engineering

-   `Features`: Features can usually be separated into numerical and categorical features

    -   `Numerical` Features

        -   `Normalization`: Normalization transforms the distribution for each feature to a similar range
            -   `Scaling`
            -   `Z-score`
        -   For distribution that follows power law, `log tranformations` can be used
        -   `Bucketing` can be used to group numerical values into categorical when the numerical value do not directly relate (e.g. longitude and latitude, zipcode)
            -   `Uniform`
            -   `Quantile`

    -   `Categorial` Features

        -   Categorical features can be converted into `one-hot` or `multi-hot` vectors
        -   `Sparse` representation can be used instead of dense representations
        -   They can also be represented as `embeddings` with continuous values

    -   Feature Crosses

        Feature crosses are used to introduce `non-linear` relationships between features to engineer new features.

- `Labels`

    For supervised learning, labels should also be inspected and reviewed. Labels can be categorized into `direct` or `derived` based on their source and ML problem definition. An example for direct labels is movie rating and an example for derived label is users watched movies. See https://developers.google.com/machine-learning/data-prep/construct/collect/label-sources for more information.

    For labels, check the distribution to identify `class imbalances`.

    -   Class Imbalance:

        To overcome class imbalance, downsampling and upsampling techniques can be used

        -   `Downsampling`: downsample the majority class but upweight the samples
        -   https://developers.google.com/machine-learning/data-prep/construct/sampling-splitting/imbalanced-data
        -   `Upsampling`: upsample the minority class by bootstrapping
        -   Additionally, for image segmentation, biased random crop can be used
        -   https://developer.nvidia.com/blog/accelerating-medical-image-processing-with-dali/

        Additionally, one can use weighted loss function and other metrics (`precision` and `recall`) to evaluate the model with class imbalanced data.

        Labels can also be grouped to alleviate class imbalance and change the ML problem.

-   `Outliers`

    For both features and labels, check for outliers, missing values, and other mistakes.

    -   Feature outliers can be `clipped`
    -   Missing data can be `imputed` by mean or most frequent value
    -   If too many observations are missing the feature, the feature can be `discarded`
    -   Check for incorrect entries such as typos
    -   For labels, check whether all the entries are in `expected range`
    -   Check every case for label correctness if possible, otherwise spot check
    -   For missing label, ask for annotation or discard the observation

-   `Correlations`

    Additionally, for supervised learning, check the correlation between features and labels. Identify feature highly correlated with labels and use them to establish an early baseline performance.

    -   Check the correlation among all the features to identify highly-correlated feature, which can be removed
    -   Check the correlation between features and labels to gain a early understanding of the predictability of the features
    -   Note that correlation only finds linear relationships, `mutual information` can be used to find more complex relationships
    -   Correlation is only applicable to univariate analysis. For multi-variate, `feature selection` techniques can be used later in the pipeline

<!---  Data Centric --->

## Generalization

A successful ML model needs to perform well on new and unseen data. In other words, it needs to `generalize` well. In order to test the model generalization, the dataset is splitted into several partitions, `train`, `development (dev)` / `validation (val)`, `test` sets. Train set is used to train the model. Dev set is used to tune the hyperparameters to detect overfitting and quantifies generalizability. Test sets are used to evaluate performance. Dev sets are used so the model never sees the test set for unbiased evaluation. See https://developers.google.com/machine-learning/crash-course/validation/another-partition for more information. This is referred to as `hold-out` validation.

Ideally, distribution of train / dev / test should follow the following properties,

-   Random independent identically distributed (iid)
-   Stationary distribution
-   Same Distribution

Traditionally, the data is `randomly` splitted into approximately 70% for train 10% for dev and 20% for test. Note that for ML problems, the size of dev and test sets need to be big enough for an unbiased evalution of performance. When the data size is big enough, the majority of data can be used for train and leave smaller portions for dev and test sets. For example, a dataset with one million examples 98% can be used for training, and 1% for dev set, 1% for test set still has 10,000 examples.

Typically, the data is randomly shuffled before splitting. However, random splitting is not ideal in certain scenarios. For example, class imbalance, clustered, and time dependent data. See https://developers.google.com/machine-learning/crash-course/18th-century-literature for more details. For randomization, always `seed` the sampling for reproducible results.

When the dataset is small, `k-fold` cross validation is often used to give a better estimate. K-fold cross validation first splits the dataset into k partitions, and trains k models each with one of the partitions left out. The final performance is averaged across all models. `Leave-one-out` cross validation is a special case where k is the sample size.

The objective of cross validation is to check whether the model is overfitting to the train set and does not generalizes well.

### Variance / Overfitting

`Overfitting` happens when the model capacity is big enough and memorizes the train set. When tested with the dev or test set, the perfomance drops significantly and is therfore not useful. Overfitting is referred to model having `high variance`, with variance being a property of an estimator. It can be described as how much the estimator varies as a function of a data sample.

There are many ways to address overfitting, the most common is `regularization`. Increasing the dataset size can also help the model reach statistical efficiency.

### Bias / Underfitting

Another property of an estimator is the `bias`, it can be described as how much the estimator differs from the truth. When a model has high bias, it means the model is fitting the traing set poorly, also known as `underfitting`.

The most common way to address high bias is to increase the hypothesis space or increase model capacity. This can be done by `adding more features`, or `build bigger models` in neural network. The downside is the risk of overfitting.

The relationship between bias and variance is often seen as a trade-off. But it is more of finding the optimal model capacity so that both the bias and generalization error is low.

To detect overfitting, it is helpful to monitor the training loss and validation loss while training.

### Regularization

A ML model find the optimal parameters by minimizing the prediction and the provided labels. This is referred to as
`Empirical Risk Minimization`. A common way to address overfitting is to add regularization terms to the optimization problem, or `Structural Risk Minimization`.

Two regularization terms are commonly used,

-   `L1` (LASSO) pushes weights to zero to encourage `sparsity`
-   `L2` (ridge) pushes weights near zero to encourage `stability`, also known as `weight decay`
-   Elastic nets combines both L1 and L2
-   L1 and L2 are also used for feature selection

Besides regularization, other techniques can help detect and reduce overfitting.

-   Early Stopping: which the user defines criteria for stopping the model training
-   SVM utilizes the C coefficient along with L1 / L2
-   Decision Tress can be regularized by `pruning`, tree `depth` and number of trees
-   Neural networks can use `Dropout` layers

### Metrics

Metrics are used to compare model performance. It is important to choose a metric that truly represents the objective of the model. Choose a single metric to evaluate but others can also be collected. For classification problems, it is typical to use `accuracy: (TP + TN) / (TP + FP + TN + FN)`. For class imbalanced problems, `precision: TP / (TP + FP)` and `recall: TP / (TP + FN)` may be more informative. Increasing the threshold leads to less False Positives and result in higher precision, while decreasing the threshold leads to less False Negatives with higher Recall. `F1 / Dice Score: 2 x P x R / (P + R)` is the harmonic mean of precision and recall. It is also commonly used in image segmentation along with `Hausdorff Distance`. `Jaccard Index / Intersection over Union (IoU)` is used for object detection and categorical features.

Besides single value metrics, `Receiver Operating Characteristic (ROC) Curve` assess model performance at different threshold values and `Area Under the Curve (AUC)` quantifies the curve. `Calibration Plot` visualizes the performance with different labels to detect `Bucketed Bias`.

## Model

In supervised learning, models use `parameters` $\theta$ and the `examples` x to form the `hypothesis` and make `predictions` $\hat{y}$ and compare with the `labels` y. The `Loss` function quantifies the difference between $\hat{y}$ and y to provide updates to $\theta$ to minimize the difference. The `Cost` function is the loss function for the entire train set. Optimal parameters $\theta$* an be found by `iterative` methods such as `Gradient Descent` that utilizes the differences between  y and $\hat{Y}$ to update $\theta$.

Models can be categorized into `Discriminative` and `Generative` based on their assumptions. Additionally, `parametric` models refer to models with fixed set of parameters while `non-parametric` models have number of parameters that grows with data size.

Examples X are often represented in `design matrix` with rows being examples (m) and columns as features (n). Parameters $\theta$ represents the weight for each feature. Predictions are therfore $\hat{Y}$ = X $\theta$. Equations below uses single example for clarity.

### Discriminative Models

Discriminative models find the conditional probability of y given x parameterized by $\theta$, P(y | x; $\theta$).

-   `Linear Regression` (Exponential family) follows the form $\hat{y}$ = $\theta$<sup>T</sup>x with x<sub>0</sub> being 1 and $\theta$<sub>0</sub> being the bias term. It commonly uses `Minimum Squared Error` (MSE) as the Loss term, (y - $\hat{y}$)<sup>2</sup> which can be derived from `Maximum Likelihood Estimation (MLE)` with `Gaussian` distribution. Besides iterative methods, Linear Regression can also be solved using analytical methods such as  Normal equation to find $\theta$* in one step with $\theta$* = (X<sup>T</sup>X)<sup>-1</sup>X<sup>T</sup>y, given that (X<sup>T</sup>X) is invertible. Note that matrix inverses are expensive operation and prone to numerical errors.

-   `Locally Weighted Linear Regression` (Non-Parametric) weighs the individual loss by non-negative function w(i) based on their distance to the point of prediction.

-   `Logistic Regression` (Exponential family) can be used to predict probabilities and is often used for `binary classification` with probability threshold. It follows the form $\hat{y}$ = $\sigma$ (z) with $\sigma$ as the `sigmoid/logistic` function, $\sigma$ (z) = 1/(1+e<sup>-z</sup>) and z = $\theta$<sup>T</sup>x. The probability resembles the `Bernoulli` distribution, P(y = x; $\theta$) = $\hat{y}$ <sup>y</sup> (1 - $\hat{y}$) <sup> (1-y) </sup>. `Regularization` is `extremely important` for Logistic Regression as the sigmoid function reaches asymptotic when z approaches +/- infinity. Without regularization, the parameters may explode and/or vanish. The loss function is the $\prod$ P(y = x; $\theta$) and is usually applied by a logarithmic to become `log likelihood` which becomes $\sum$ of all examples P(y = x; $\theta$) = y log($\hat{y}$) + (1-y) log((1 - $\hat{y}$)). This loss is also know as `cross entropy loss (XEnt)`. `Maximum Likelihood Estimation` maximizes the log likelihood with gradient ascent, but is usually transformed to `minimizing negative log likelihood` with `gradient descent`.

-   `Softmax Regression` is logistic regression with `multi-class` classification. The logits (z, $\theta$<sup>T</sup>x) are exponentialized and normalized so the probabilities sums to 1, (e<sup>$\theta$<sub>i</sub><sup>T</sup>x</sup> / $\sum_j$ e<sup>$\theta$<sub>j</sub><sup>T</sup>x</sup>). The loss function become `categorical cross entropy`. For problems with `multi-class single instance`, softmax is used and `multi-class multi-instance`, logistic regression is used for each instance.

-   Generalized Linear Models (Exponential family)

-   Support Vector Machines (SVM)
-   Neural Networks (NN)
-   Decision Trees
-   Ensembles
    -   Boosting: Adaptive Boosting (AdaBoost), Gradient Boosting Machines (GBM), Extreme Gradient Boosting (XGBoost)
    -   Bagging: Random Forest (RF)

-   K Nearest Neighbors (Non-Parametric)
-   K Means (Clustering, Non-Parametric)

-   Generative
    -   Gaussian Discriminant Analysis
    -   Naive Bayes

-   Estimators:
    -   Maximimum Likelihood Estimation (MLE, frequentist):
    -   Maximum A Posteriori (MAP, bayesian):

Depending on the update scheme,

-   Optimizers:

    -   Iterative Methods
        -   Gradient Descent
            -   Batch Gradient Descent
            -   Mini-Batch Gradient Descent
            -   Stochastic Gradient Descent

        -   Momentum
        -   Adaptive Learning Rate
        -   Momentum + Adaptive Learning Rate
        -   Newton-Raphson

    -   Direct / Analytical Methods
        -   Normal Equation