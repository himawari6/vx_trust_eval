import requests
from datetime import datetime, timedelta

POLICY_URL = "http://10.26.36.254:9090/v1/trust/assessments"

EFFECT = {
    "允许访问": "allow",
    "二次认证": "deny",
    "限制访问": "deny",
    "封禁": "deny"
}

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

def push_single_policy(user_id: str, trust_score: float, action: str, vm_id: str, policy_id: int):
    now = datetime.now()
    payload = {
        "assessment_id": "1",  # 先固定 1
        "user_id": user_id,
        "trust_score": round(trust_score, 4),
        "policy": {
            "policy_id": policy_id,
            "policy_name": "访问控制",
            "submitted_by": "信任评估模块",
            "subject": {
                "user_id": user_id,
                "tunnel_id": "1",
                "mac_address": "default",
                "ip_address": "default"
            },
            "resource": {
                "vm_id": vm_id
            },
            "operation": "vGTP",
            "effect": EFFECT.get(action, "deny"),
            "valid_until": (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        },
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
    }
    resp = requests.post(POLICY_URL, json=payload, timeout=5)
    return resp.status_code, resp.json()


def push_policy(graph):
    # 从graph中的连接信息获取该用户使用了哪些虚拟机，便于细粒度管控
    user_vm_map = graph.extract_user_vm_ids_map()

    # graph的用户列表导出用户->策略对应关系
    user_action_map = graph.extract_user_action_map()

    results = []
    policy_id = 2
    for user_id, user in graph.users.items():

        vm_ids = user_vm_map[user_id]
        if not vm_ids:
            vm_ids = {"all"}

        action = user_action_map[user_id]

        trust_score = user.trust_score

        current_user_result = []
        for vm_id in vm_ids:
            status, res = push_single_policy(
                user_id=user_id,
                trust_score=trust_score,
                action=action,
                vm_id=vm_id,
                policy_id=policy_id
            )
            policy_id = policy_id + 1
            current_user_result.append({
                "vm_id": vm_id,
                "status": status,
                "response": res
            })
        results.append({
            "user_id": user_id,
            "trust_score": trust_score,
            "action": action,
            "pushed_policies": current_user_result
        })
    
    return results




