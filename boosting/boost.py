import argparse
import numpy as np 
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import Perceptron
from sklearn.base import clone 
import matplotlib.pyplot as plt

np.random.seed(1234)

class FoursAndNines:
    """
    Class to store MNIST data
    """

    def __init__(self, location):

        import cPickle, gzip

        # Load the dataset
        f = gzip.open(location, 'rb')

        # Split the data set 
        train_set, valid_set, test_set = cPickle.load(f)

        # Extract only 4's and 9's for training set 
        self.x_train = train_set[0][np.where(np.logical_or( train_set[1]==4, train_set[1] == 9))[0],:]
        self.y_train = train_set[1][np.where(np.logical_or( train_set[1]==4, train_set[1] == 9))[0]]
        self.y_train = np.array([1 if y == 9 else -1 for y in self.y_train])
        
        # Shuffle the training data 
        shuff = np.arange(self.x_train.shape[0])
        np.random.shuffle(shuff)
        self.x_train = self.x_train[shuff,:]
        self.y_train = self.y_train[shuff]

        # Extract only 4's and 9's for validation set 
        self.x_valid = valid_set[0][np.where(np.logical_or( valid_set[1]==4, valid_set[1] == 9))[0],:]
        self.y_valid = valid_set[1][np.where(np.logical_or( valid_set[1]==4, valid_set[1] == 9))[0]]
        self.y_valid = np.array([1 if y == 9 else -1 for y in self.y_valid])
        
        # Extract only 4's and 9's for test set 
        self.x_test  = test_set[0][np.where(np.logical_or( test_set[1]==4, test_set[1] == 9))[0],:]
        self.y_test  = test_set[1][np.where(np.logical_or( test_set[1]==4, test_set[1] == 9))[0]]
        self.y_test = np.array([1 if y == 9 else -1 for y in self.y_test])
        
        f.close()

class AdaBoost:
    def __init__(self, n_learners=20, base=DecisionTreeClassifier(max_depth=1)):
        """
        Create a new adaboost classifier.
        
        Args:
            n_learners (int, optional): Number of weak learners in classifier.
            base (BaseEstimator, optional): Your general weak learner 

        Attributes:
            base (estimator): Your general weak learner 
            n_learners (int): Number of weak learners in classifier.
            alpha (ndarray): Coefficients on weak learners. 
            learners (list): List of weak learner instances. 
        """
        
        self.n_learners = n_learners 
        self.base = base
        self.alpha = np.zeros(self.n_learners)
        self.learners = []
        
    def fit(self, X_train, y_train):
        """
        Train AdaBoost classifier on data. Sets alphas and learners. 
        
        Args:
            X_train (ndarray): [n_samples x n_features] ndarray of training data   
            y_train (ndarray): [n_samples] ndarray of data 
        """

        m = len(y_train)
        w = np.ones(m)
        for i in range(self.n_learners):
            h = clone(self.base)
            h.fit(X_train, y_train, sample_weight=w)
            acc = h.score(X_train, y_train, sample_weight=w)
            self.alpha[i] = 0.5*np.log(acc/(1-acc))
            self.learners.append(h)
            # update the weight
            for j in range(m):
                w[j]*=np.exp(-self.alpha[i]*y_train[j]*h.predict(X_train[j])[0])
    def predict(self, X):
        """
        Adaboost prediction for new data X.
        
        Args:
            X (ndarray): [n_samples x n_features] ndarray of data 
            
        Returns: 
            [n_samples] ndarray of predicted labels {-1,1}
        """

        answer=np.zeros(len(X))
        for i in range(len(X)):
            p = 0
            for a, h in zip(self.alpha ,self.learners):
                p+=a*h.predict(X[i])
                answer[i] = np.sign(p)
        return answer
    
    def score(self, X, y):
        """
        Computes prediction accuracy of classifier.  
        
        Args:
            X (ndarray): [n_samples x n_features] ndarray of data 
            y (ndarray): [n_samples] ndarray of true labels  
            
        Returns: 
            Prediction accuracy (between 0.0 and 1.0).
        """

        # TODO 
        acc = 0
        for px, yy in zip(self.predict(X), y):
            if px==yy:
                acc+=1

        return float(acc)/len(y)
    
    def staged_score(self, X, y):
        """
        Computes the ensemble score after each iteration of boosting 
        for monitoring purposes, such as to determine the score on a 
        test set after each boost.
        
        Args:
            X (ndarray): [n_samples x n_features] ndarray of data 
            y (ndarray): [n_samples] ndarray of true labels  
            
        Returns: 
            [n_learners] ndarray of scores 
        """

        # TODO 
        p = np.zeros(len(X))
        stage_score = np.zeros(self.n_learners)
        for i in range(self.n_learners):
            for j in range(len(X)):
                p[j]+=self.alpha[i]*self.learners[i].predict(X[j])[0]
                if np.sign(p[j])==y[j]:
                    stage_score[i]+=float(1)/len(X)
        return stage_score


def mnist_digit_show(flatimage, outname=None):

	import matplotlib.pyplot as plt

	image = np.reshape(flatimage, (-1,28))

	plt.matshow(image, cmap=plt.cm.binary)
	plt.xticks([])
	plt.yticks([])
	if outname: 
	    plt.savefig(outname)
	else:
	    plt.show()

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='AdaBoost classifier options')
	parser.add_argument('--limit', type=int, default=-1,
                        help="Restrict training to this many examples")
	parser.add_argument('--n_learners', type=int, default=50,
                        help="Number of weak learners to use in boosting")
	args = parser.parse_args();
    	data = FoursAndNines("../data/mnist.pkl.gz")
    # An example of how your classifier might be called 
	clf = AdaBoost(n_learners=400, base=DecisionTreeClassifier(max_depth=1, criterion="entropy"))
    	clf.fit(data.x_train, data.y_train)
    	stage_score_train = [1]*400-clf.staged_score(data.x_train, data.y_train)
    	stage_score_test = [1]*400-clf.staged_score(data.x_test, data.y_test)
	plt.plot(stage_score_train, label='train')
    	plt.plot(stage_score_test, label='test')
    	plt.xlabel('iterations')
    	plt.ylabel('accuracy')
        plt.legend()
    	plt.grid(True)



