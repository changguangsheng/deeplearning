import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

"""
    sdf

"""

def initialize_parameters(layer_dims):
    """
    :param layer_dims: list , 每一层单元的个数
    :return: dictionary ，存储参数W1...WL b1....bL
    """
    np.random.seed(3)
    L = len(layer_dims)#the number of layers in the network
    parameters = {}
    for l in range(1,L):
        parameters["W" + str(l)] = np.random.randn(layer_dims[l], layer_dims[l - 1]) * np.sqrt(1 / layer_dims[l - 1])  # xavier initialization
        parameters["b" + str(l)] = np.zeros((layer_dims[l], 1))
    return parameters

#RELU
def relu(Z):
    """

    :param Z: Output of the linear layer
    :return: A: Output of activation
    """
    A = np.maximum(0,Z)
    return A

#Sigmoid
#implement the activation function(ReLU and sigmoid)
def sigmoid(Z):
    """

    :param Z:Output of the linear layer
    :return:
    """
    A = 1/(1 + np.exp(-Z))
    return A

def forward_propagation(X , parameters):
    """

    :param X: input dataset , of shape(input size , nnumber of examples)
    parameters -- python dictionary containing your parameters "W1", "b1", "W2", "b2",...,"WL", "bL"
                    W -- weight matrix of shape (size of current layer, size of previous layer)
                    b -- bias vector of shape (size of current layer,1))
    :return:
    AL : the output of the last Layer(y_predict)
	caches: list, every element is a tuple:(W,b,z,A_pre)
    """
    L = len(parameters)//2
    A = X
    caches = [(None,None,None,X)] # 第0层(None,None,None,A0) w,b,z用none填充,下标与层数一致，用于存储每一层的，w,b,z,A
    #calculate from 1 to L-1 layer
    for l in range(1 , L):
        A_pre = A
        W = parameters['W' + str(l)]
        b = parameters['b' + str(l)]
        #计算Z = w * x + b
        z = np.dot(W , A_pre) + b
        A = relu(z)
        caches.append((W,b,z,A))
    #calculate Lth layer
    WL = parameters['W'+str(L)]
    bL = parameters['b'+str(L)]
    zL = np.dot(WL ,A) +bL
    AL = sigmoid(zL)
    caches.append((WL ,bL, zL,AL))
    return AL , caches


#带dropout的深度神经网络
def forward_propagation_with_dropout(X , parameters , keep_prob = 0.8):
    """

    :param X: input dataset, of shape (input size, number of examples)
    :param parameter:  python dictionary containing your parameters "W1", "b1", "W2", "b2",...,"WL", "bL"
                    W -- weight matrix of shape (size of current layer, size of previous layer)
                    b -- bias vector of shape (size of current layer,1)
    :param keep_prob: probability of keeping a neuron active during drop-out, scalar

    :return:
        AL: the output of the last Layer(y_predict)
    	caches: list, every element is a tuple:(W,b,z,A_pre)
    """
    np.random.seed(1)
    # number of layer
    L = len(parameters)//2
    A = X
    # 用于存储每一层的，w,b,z,A,D第0层w,b,z用none代替
    caches = [(None,None,None,X,None)]
    #calculate from 1 to L-1 layer
    for l in range(1 , L):
        A_pre = A
        W = parameters['W' + str(l)]
        b = parameters['b' + str(l)]
        z = np.dot(W ,A_pre) + b
        A = relu(z)
        # initialize matrix D
        D = np.random.randn(A.shape[0] ,A.shape[1])
        D = (D < keep_prob)
        A = np.multiply(A,D)
        A = A / keep_prob
        caches.append((W,b,z,A,D))
    #calculate Lth layer
    WL = parameters["W" + str(L)]
    bL = parameters["b" + str(L)]
    zL = np.dot(WL , A) + bL
    AL = sigmoid(zL)
    caches.append((WL , bL ,zL,AL))
    return AL ,caches

#calculate cost function
def compute_cost(AL , Y):
    """

    :param AL: 最后一层激活只,即预测值, shape:(1,number of examples)
    :param Y: 真实值 ,shape(1 , number of examples)
    :return:
    """
    m = Y.shape[1]
    cost = 1. / m * np.nansum(np.multiply(-np.log(AL + 1e-5), Y) + np.multiply(-np.log(1 - AL + 1e-5), 1 - Y))
    #从数组的形状中删除单位条目，即把shape中为1的维度去掉,比如把[[[2]]]变成2

    cost = np.squeeze(cost)

    return cost

def relu_backward(Z):
    """

    :param Z: the input of activation
    :return:
    """
    dA = np.int64(Z > 0)
    return dA

#derivation of relu
def backward_propagation_with_dropout(AL , Y , caches ,keep_prob = 0.8):
    """
        Implement the backward propagation presented in figure 2.
		Arguments:
		X -- input dataset, of shape (input size, number of examples)
		Y -- true "label" vector (containing 0 if cat, 1 if non-cat)
		caches -- caches output from forward_propagation(),(W,b,z,pre_A)
		Returns:
		gradients -- A dictionary with the gradients with respect to dW,db
    """
    m = Y.shape[1]
    L = len(caches) - 1
    #print("L : " + str(L))
    #calculate the Lth layer gradients
    prev_AL = caches[L-1][3]
    dzL = 1. / m * (AL  - Y)
    #print(dzL.shape)
    #print(prev_AL.T.shape)
    dWL = np.dot(dzL ,prev_AL.T)
    dbL = np.sum(dzL ,axis= 1 , keepdims=True)
    gradients ={"dW" +str(L) :dWL , "db" + str(L) : dbL}
    #calculate from L-1 to 1 layer gradients
    for l in reversed(range(1,L)):#L-1 , L -2..1
        post_W = caches[l+1][0]
        dz = dzL #用最后一层的dz
        #print(post_W.T.shape)
        #print(dz.shape)
        dal = np.dot(post_W.T, dz)
        Dl = caches[l][4]
        dal = np.multiply(dal, Dl)  # Apply mask Dl to shut down the same neurons as during the forward propagation
        dal = dal / keep_prob  # Scale the value of neurons that haven't been shut down
        z = caches[l][2]
        dzl = np.multiply(dal ,relu_backward(z))
        prev_A = caches[l-1][3]
        dWl = np.dot(dzl ,prev_A.T)
        dbl = np.sum(dzl ,axis= 1 ,keepdims= True)

        gradients['dW' + str(l)] = dWl
        gradients['db' + str(l)] = dbl
        dzL = dzl #更新dz
    return gradients

def update_parameters(parameters , grades , learning_rate):
    """

    :param parameters: dictionary , w , b
    :param grades: dw ,db
    :param learning_rate: alpha
    :return:
    """
    L = len(parameters)//2
    for l in range(L):
        parameters['W' + str(l + 1)] = parameters['W' + str(l + 1)]  - learning_rate *  grades['dW' + str(l + 1)]
        parameters['b' + str(l + 1)] = parameters['b' + str(l + 1)] - learning_rate * grades['db' + str(l + 1)]
    return  parameters

def L_layer_model(X , Y ,layer_dims , learning_date , num_iterations,keep_prob):
    """

    :param X:
    :param Y:
    :param layer_dims:list containing the input size and each layer size
    :param learning_date:
    :param num_iterations:
    :param keep_prob:
    :return:
    """
    costs = []
    parameters = initialize_parameters(layer_dims)
    for i in range(0 , num_iterations):
        AL , caches = forward_propagation_with_dropout(X,parameters,keep_prob)
        #calaulate the cost
        cost  = compute_cost(AL ,Y)
        if i % 1000 == 0:
            print("Cost after iteration {}: {}" .format(i ,cost))
            costs.append(cost)
        #backward paopagation
        grads = backward_propagation_with_dropout(AL,Y,caches,keep_prob)
        #update propagation
        parameters = update_parameters(parameters,grads ,learning_date)
    print("length of cost")
    print(len(costs))
    plt.clf()
    plt.plot(costs) #o- :圆形
    plt.xlabel("iterations(thousand)") #横坐标名字
    plt.ylabel("cost") #纵坐标名字
    plt.show()
    return parameters

#predict function
def predict(X_test , y_test ,parameters):
    """

    :param x_test:
    :param y_test:
    :param parameters:
    :return:
    """
    m = y_test.shape[1]
    Y_prediction = np.zeros((1,m))
    prob ,caches = forward_propagation(X_test ,parameters)
    for i in range(prob.shape[1]):
# Convert probabilities A[0,i] to actual predictions p[0,i]
### START CODE HERE ### (≈ 4 lines of code)
        if prob[0,i] > 0.5 :
            Y_prediction[0,i] = 1
        else:
            Y_prediction[0,i] = 0
    accuracy = 1 - np.mean(np.abs(Y_prediction - y_test))
    return  accuracy
#DNN model
def DNN(X_train,y_train,X_test,y_test,layer_dims , learning_rate = 0.001,num_iterations=20000,keep_prob = 1):
    parameters = L_layer_model(X_train,y_train,layer_dims,learning_rate,num_iterations,keep_prob)
    accuracy = predict(X_test ,y_test ,parameters)
    return  accuracy
if __name__ == "__main__":
    X_data, y_data = load_breast_cancer(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, train_size=0.8, random_state=28)
    X_train = X_train.T
    y_train = y_train.reshape(y_train.shape[0], -1).T
    X_test = X_test.T
    y_test = y_test.reshape(y_test.shape[0], -1).T
    # X_train, y_train, X_test, y_test = load_2D_dataset()
    accuracy = DNN(X_train, y_train, X_test, y_test, [X_train.shape[0], 10, 5, 1], keep_prob=0.86)
    print(accuracy)
    # X_assess, parameters = forward_propagation_with_dropout_test_case()
    #
    # A3, cache = forward_propagation_with_dropout(X_assess, parameters, keep_prob=0.7)
    # print("A3 = " + str(A3))



