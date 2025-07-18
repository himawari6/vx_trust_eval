from config import EPS, weights
from models.graph import Graph
from models.user import ProcessedUser
from models.terminal import ProcessedTerminal
from models.vm import ProcessedVM
import numpy as np
from math_utils import sigmoid


# ---------------- 第一部分：节点初始信任值计算 ----------------
def compute_user_base_trust(user: ProcessedUser):
    """
    计算用户节点基础信任值（不含汇聚部分）
    """
    w1, w2, w3 = weights["w1"], weights["w2"], weights["w3"]
    user.trust_score = (
        w1 * user.login_score +
        w2 * user.time_score +
        w3 * user.env_score
    )
    return user.trust_score

def compute_terminal_initial_trust(terminal: ProcessedTerminal):
    """
    计算接入终端节点初始信任值
    """
    w4, w5 = weights["w4"], weights["w5"]
    terminal.trust_score = (
        w4 * terminal.basic_score +
        w5 * terminal.alert_score_terminal
    )
    return terminal.trust_score

def compute_vm_initial_trust(vm: ProcessedVM):
    """
    计算虚拟机节点初始信任值
    """
    w6, w7, w8, w9 = weights["w6"], weights["w7"], weights["w8"], weights["w9"]
    vm.trust_score = (
        w6 * vm.os_score +
        w7 * vm.performance_score +
        w8 * vm.connection_score +
        w9 * vm.alert_score_VM
    )
    return vm.trust_score


# ---------------- 第二部分：构建Graph结构 ----------------

def build_graph(users, terminals, vms, connections):
    """
    统一构建Graph结构，录入节点与连接数据，
    传入指定范围的数据，可确保适用于全部用户和局部用户的信任评估
    """
    graph = Graph()

    for user in users:
        compute_user_base_trust(user)
        graph.add_user(user)

    for terminal in terminals:
        compute_terminal_initial_trust(terminal)
        graph.add_terminal(terminal)

    for vm in vms:
        compute_vm_initial_trust(vm)
        graph.add_vm(vm)

    for conn in connections:
        # conn为连接对象或dict，提取必要信息
        user_id = conn.user_id if hasattr(conn, 'user_id') else conn["user_id"]
        terminal_id = conn.terminal_id if hasattr(conn, 'terminal_id') else conn["terminal_id"]
        vm_id = conn.vm_id if hasattr(conn, 'vm_id') else conn["vm_id"]
        online_time = conn.onlineTime if hasattr(conn, 'onlineTime') else conn["onlineTime"]

        graph.add_connection(user_id, terminal_id, vm_id, online_time)

    return graph


# ---------------- 第三部分：信任汇聚计算 ----------------

def trust_propagation(graph: Graph):
    """
    执行图结构的信任值汇聚，更新终端与用户信任值
    """

    for user_id, user in graph.users.items():
        # 返回字典，键为终端号k，值为k号终端连接虚拟机的总时间C(k)，维数1*N，N为终端数量，共N个键值对
        # 若未访问任何终端、虚拟机，返回一个空字典{}
        terminal_time_map = graph.get_user_terminals_time(user_id)

        if not terminal_time_map:
            # 计算衰减
            user.trust_score = user.trust_score - 0.2 * sigmoid(user.loginTimeDiff / 12)
            continue  # 无连接，基础信任值即为总信任值

        # log求和得到该用户连接终端的总时间
        total_user_time = sum(np.log(1 + value) for value in terminal_time_map.values())

        terminal_trust_sum = 0
        
        # 对于该用户下的每个终端
        for terminal_id, term_time in terminal_time_map.items():
            # 获取该用户、该终端下对每个虚拟机的访问时间列表
            # 返回字典，键为虚拟机号m，值为w(k,m)，维数1*M，共M个键值对
            vm_time_map = graph.get_terminal_vms_time(user_id, terminal_id)
            # log求和得到该用户该终端连接虚拟机的总时间
            total_term_time = sum(np.log(1 + value) for value in vm_time_map.values())

            if total_term_time < EPS:
                terminal_effective_score = graph.terminals[terminal_id].trust_score
            else:
                # 根据w(m,k)对虚拟机加权求和
                vm_trust_sum = sum(
                    graph.vms[vm_id].trust_score * (np.log(1 + vm_time) / total_term_time)
                    for vm_id, vm_time in vm_time_map.items()
                    if vm_id in graph.vms
                )
                # 混合自身分数和虚拟机求和结果，得到该用户、该终端的Ttrust(k)
                terminal_effective_score = (
                    0.5 * graph.terminals[terminal_id].trust_score + 
                    0.5 * vm_trust_sum
                )

            # 根据C(k)对终端加权求和
            terminal_trust_sum += terminal_effective_score * (np.log(1 + term_time) / total_user_time)

        # 混合自身分数和终端求和结果，得到该用户的Tuser
        user.trust_score = (
            0.5 * user.trust_score + 
            0.5 * terminal_trust_sum - 
            0.2 * sigmoid(user.loginTimeDiff / 12)
        )