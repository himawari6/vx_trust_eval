# 策略生成
def generate_action(user):
    """
    根据用户信任值和门限值返回访问策略
    """
    T = user.trust_score
    threshold = user.thresholdDelta

    if T > threshold:
        return "允许访问"
    elif T > threshold - 0.25:
        return "二次身份认证"
    elif T > threshold - 0.5:
        return "限制访问"
    else:
        return "封禁用户"   

def generate_policy_signal(processed_users):
    """
    生成最终结果结构：{user_id: {trust: float, action: str}}
    """
    result = {}
    for user in processed_users:
        result[user.user_id] = {
            "trust": user.trust_score,
            "action": generate_action(user)
        }
    # 返回字典，键为用户id，值为用户信任值、采取的动作
    return result