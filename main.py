from data_retriever import get_all_data, get_specific_data
from preprocess import aggregate_alerts, preprocess_user, preprocess_terminal, preprocess_vm
from trust_algorithm import build_graph, trust_propagation, generate_policy

from models.user import RawUser
from models.terminal import RawTerminal
from models.vm import RawVM

# ---------------- 全量用户信任评估 ----------------

def evaluate_all_users():
    """
    获取全量数据，执行所有用户的信任评估
    :return: dict {user_id: 最终信任值}
    """
    raw_users, raw_terminals, raw_vms, connections = get_all_data()

    # print(raw_users)
    # print(raw_terminals)
    # print(raw_vms)
    # print(connections)
    # 特征预处理
    aggregate_alerts(connections, raw_terminals, raw_vms)

    # print(raw_users)
    # print(raw_terminals)
    # print(raw_vms)

    users = [preprocess_user(u) for u in raw_users]
    terminals = [preprocess_terminal(t) for t in raw_terminals]
    vms = [preprocess_vm(vm) for vm in raw_vms]

    # print(users)
    # print(terminals)
    # print(vms)

    # 构建图 & 评估
    graph = build_graph(users, terminals, vms, connections)
    trust_propagation(graph)

    results = generate_policy(users)

    return results

def evaluate_specific_user(user_id, terminal_ids, vm_ids):
    """
    仅针对指定用户、终端、虚拟机的信任评估
    :param user_id: 用户ID
    :param terminal_ids: 终端ID列表
    :param vm_ids: 虚拟机ID列表
    :return: 指定用户的最终信任值
    """
    raw_users, raw_terminals, raw_vms, connections = get_specific_data(user_id, terminal_ids, vm_ids)

    if not raw_users:
        raise ValueError(f"用户 {user_id} 不存在")

    aggregate_alerts(connections, raw_terminals, raw_vms)
    users = [preprocess_user(u) for u in raw_users]
    terminals = [preprocess_terminal(t) for t in raw_terminals]
    vms = [preprocess_vm(vm) for vm in raw_vms]

    graph = build_graph(users, terminals, vms, connections)
    final_scores = trust_propagation(graph)

    return final_scores.get(user_id)


if __name__ == '__main__':
    print(evaluate_all_users())