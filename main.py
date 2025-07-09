from data_retriever import get_all_data, get_user_data
from preprocess import preprocess_user, preprocess_terminal, preprocess_vm
from trust_algorithm import build_graph, trust_propagation

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

    # 特征预处理
    users = [preprocess_user(u) for u in raw_users]
    terminals = [preprocess_terminal(t) for t in raw_terminals]
    vms = [preprocess_vm(vm) for vm in raw_vms]

    # 构建图 & 评估
    graph = build_graph(users, terminals, vms, connections)
    final_scores = trust_propagation(graph)

    return final_scores

def evaluate_specific_user(user_id, terminal_ids, vm_ids):
    """
    仅针对指定用户、终端、虚拟机的信任评估
    :param user_id: 用户ID
    :param terminal_ids: 终端ID列表
    :param vm_ids: 虚拟机ID列表
    :return: 指定用户的最终信任值
    """
    raw_users, raw_terminals, raw_vms, connections = get_user_data(user_id, terminal_ids, vm_ids)

    if not raw_users:
        raise ValueError(f"用户 {user_id} 不存在")

    users = [preprocess_user(u) for u in raw_users]
    terminals = [preprocess_terminal(t) for t in raw_terminals]
    vms = [preprocess_vm(vm) for vm in raw_vms]

    graph = build_graph(users, terminals, vms, connections)
    final_scores = trust_propagation(graph)

    return final_scores.get(user_id)
