import math

def sigmoid(x):
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 0  # 极端大负值时返回0


def generate_action(user):
    """
    根据用户信任值和门限值返回访问策略
    """
    T = user.trust_score
    threshold = user.thresholdDelta

    if T > threshold:
        return "允许访问"
    elif T > threshold - 0.5:
        return "二次身份认证"
    elif T > threshold - 0.75:
        return "限制访问"
    else:
        return "封禁用户"