import math

def sigmoid(x):
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 0  # 极端大负值时返回0
    
def relu(x):
    return max(0, x)