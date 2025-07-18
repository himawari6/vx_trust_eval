from db_utils import get_all_data, get_specific_data, update_trust_score
from preprocess import aggregate_alerts, preprocess_user, preprocess_terminal, preprocess_vm
from trust_algorithm import build_graph, trust_propagation
from policy import generate_policy

from models.user import RawUser
from models.terminal import RawTerminal
from models.vm import RawVM

import json
from log.logger import get_logger
logger = get_logger()

# ---------------- 全量用户信任评估 ----------------

def evaluate_all_users():
    """
    获取全量数据，执行所有用户的信任评估
    :return: dict {user_id: 最终信任值}
    """
    # 日志输出开始词
    logger.info("开始全部用户信任评估", extra={"extra": {"type": "all"}})

    # 从数据库读取数据建立对象
    raw_users, raw_terminals, raw_vms, connections = get_all_data()
    logger.info("原始数据", extra={"extra": {
        "type": "all",
        "raw_users": [json.dumps(u.to_dict()) for u in raw_users],
        "raw_terminals": [json.dumps(t.to_dict()) for t in raw_terminals],
        "raw_vms": [json.dumps(vm.to_dict()) for vm in raw_vms],
        "connections": [json.dumps(c.to_dict()) for c in connections]
    }})

    # 特征预处理
    aggregate_alerts(connections, raw_terminals, raw_vms)
    users = [preprocess_user(u) for u in raw_users]
    terminals = [preprocess_terminal(t) for t in raw_terminals]
    vms = [preprocess_vm(vm) for vm in raw_vms]
    logger.info("预处理后数据", extra={"extra": {
        "type": "all",
        "users": [json.dumps(u.to_dict()) for u in users],
        "terminals": [json.dumps(t.to_dict()) for t in terminals],
        "vms": [json.dumps(vm.to_dict()) for vm in vms]
    }})


    # 构建图 & 评估
    graph = build_graph(users, terminals, vms, connections)
    trust_propagation(graph)

    # 得到结果，输出/更新
    results = generate_policy(users)
    # 输出
    logger.info("评估结果", extra={"extra": {
        "type": "all",
        "results": results
    }})
    # 更新
    update_trust_score(users)
    return results

def evaluate_specific_user(user_id, terminal_ids, vm_ids):
    """
    仅针对指定用户、终端、虚拟机的信任评估
    :param user_id: 用户ID
    :param terminal_ids: 终端ID列表
    :param vm_ids: 虚拟机ID列表
    :return: 指定用户的最终信任值
    """
    # 日志输出开始词
    logger.info("开始指定用户信任评估", extra={"extra": {
        "type": "specific",
        "user_id": user_id,
        "terminal_ids": terminal_ids,
        "vm_ids": vm_ids
    }})

    raw_users, raw_terminals, raw_vms, connections = get_specific_data(user_id, terminal_ids, vm_ids)
    if not raw_users:
        raise ValueError(f"用户 {user_id} 不存在")
    logger.info("原始数据", extra={"extra": {
        "type": "all",
        "raw_users": [json.dumps(u.to_dict()) for u in raw_users],
        "raw_terminals": [json.dumps(t.to_dict()) for t in raw_terminals],
        "raw_vms": [json.dumps(vm.to_dict()) for vm in raw_vms],
        "connections": [json.dumps(c.to_dict()) for c in connections]
    }})

    aggregate_alerts(connections, raw_terminals, raw_vms)
    users = [preprocess_user(u) for u in raw_users]
    terminals = [preprocess_terminal(t) for t in raw_terminals]
    vms = [preprocess_vm(vm) for vm in raw_vms]
    logger.info("预处理后数据", extra={"extra": {
        "type": "all",
        "users": [json.dumps(u.to_dict()) for u in users],
        "terminals": [json.dumps(t.to_dict()) for t in terminals],
        "vms": [json.dumps(vm.to_dict()) for vm in vms]
    }})

    graph = build_graph(users, terminals, vms, connections)
    trust_propagation(graph)

    # 得到结果，输出/更新
    results = generate_policy(users)
    # 输出
    logger.info("评估结果", extra={"extra": {
        "type": "all",
        "results": results
    }})
    # 更新
    update_trust_score(users)
    return results