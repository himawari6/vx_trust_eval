import math
from models.user import RawUser, ProcessedUser
from models.terminal import RawTerminal, ProcessedTerminal
from models.vm import RawVM, ProcessedVM
from utils import sigmoid
from config import EPS, TAU

def aggregate_alerts(connections, raw_terminals, raw_vms):
    """
    聚合连接中的告警数，直接更新 RawTerminal 和 RawVM 实例的告警字段

    :param connections: List[Connection]
    :param raw_terminals: List[RawTerminal]
    :param raw_vms: List[RawVM]
    """
    terminal_alert_map = {}
    vm_alert_map = {}

    for conn in connections:
        tid = conn.terminal_id
        vid = conn.vm_id
        alert = getattr(conn, "alertCount", 0)

        terminal_alert_map[tid] = terminal_alert_map.get(tid, 0) + alert
        vm_alert_map[vid] = vm_alert_map.get(vid, 0) + alert

    # 写入 RawTerminal
    for t in raw_terminals:
        t.terminalAlert = terminal_alert_map.get(t.terminal_id, 0)

    # 写入 RawVM
    for v in raw_vms:
        v.VMAlert = vm_alert_map.get(v.vm_id, 0)

def preprocess_user(raw_user: RawUser):
    """用户节点特征预处理"""
    # 去除空值，置为默认
    record_id = raw_user.record_id
    user_id = raw_user.user_id
    userType = raw_user.userType if raw_user.userType is not None else 0
    thresholdDelta = raw_user.thresholdDelta if raw_user.thresholdDelta is not None else 0.8
    loginTotal = raw_user.loginTotal if raw_user.loginTotal is not None else 0
    loginSucceed = raw_user.loginSucceed if raw_user.loginSucceed is not None else 0
    ifLoginTimeOK = raw_user.ifLoginTimeOK if raw_user.ifLoginTimeOK is not None else 1
    loginTimeBias = raw_user.loginTimeBias if raw_user.loginTimeBias is not None else 0
    loginTimeDiff = raw_user.loginTimeDiff if raw_user.loginTimeDiff is not None else 0
    ifIpAllow = raw_user.ifIpAllow if raw_user.ifIpAllow is not None else 1
    ifAreaAllow = raw_user.ifAreaAllow if raw_user.ifAreaAllow is not None else 1

    # 登录次数与成功率评分
    fail_rate = (loginTotal - loginSucceed) / (loginTotal + EPS)
    login_score = 1 - fail_rate * sigmoid(loginTotal - TAU)

    # 登录时间评分
    part1 = 0.4 * (ifLoginTimeOK + 1) / 2
    part2 = 0.3 * (1 - (2 * sigmoid(abs(loginTimeBias)) - 1))
    part3 = 0.3 * (1 - (2 * sigmoid(loginTimeDiff / 43200) - 1))
    time_score = part1 + part2 + part3

    # 登录环境与网络地址评分
    env_score = 1 - (1 - ifIpAllow) / 4 - (1 - ifAreaAllow) / 4

    return ProcessedUser(
        record_id=record_id,
        user_id=user_id,
        userType=userType,
        thresholdDelta=thresholdDelta,
        loginTimeDiff=loginTimeDiff,
        login_score=login_score,
        time_score=time_score,
        env_score=env_score
    )

def preprocess_terminal(raw_terminal: RawTerminal):
    """终端节点特征预处理"""
    # 去除空值，置为默认
    terminal_id = raw_terminal.terminal_id
    terminalType = raw_terminal.terminalType if raw_terminal.terminalType is not None else 1
    userDiff = raw_terminal.userDiff if raw_terminal.userDiff is not None else 1
    terminalAlert = raw_terminal.terminalAlert if raw_terminal.terminalAlert is not None else 0
    
    # 基本信息评分
    basic_score = 1 - (terminalType - 1) / 4 - (1 - userDiff) / 4

    # 安全态势评分
    alert_score_terminal = 1 - math.tanh(terminalAlert / 10)

    return ProcessedTerminal(
        terminal_id=terminal_id,
        basic_score=basic_score,
        alert_score_terminal=alert_score_terminal
    )

def preprocess_vm(raw_vm: RawVM):
    """虚拟机节点特征预处理"""
    # 去除空值，置为默认
    vm_id = raw_vm.vm_id
    VMOsAllow = raw_vm.VMOsAllow if raw_vm.VMOsAllow is not None else 1
    VMOsVersionAllow = raw_vm.VMOsVersionAllow if raw_vm.VMOsVersionAllow is not None else 1
    CPU = raw_vm.CPU if raw_vm.CPU is not None else 1
    mem = raw_vm.mem if raw_vm.mem is not None else 1
    VMLoginTotal = raw_vm.VMLoginTotal if raw_vm.VMLoginTotal is not None else 0
    VMLoginSucceed = raw_vm.VMLoginSucceed if raw_vm.VMLoginSucceed is not None else 0
    VMConnectionUser = raw_vm.VMConnectionUser if raw_vm.VMConnectionUser is not None else 0
    VMAlert = raw_vm.VMAlert if raw_vm.VMAlert is not None else 0

    # 系统信息评分
    os_score = 1 - (1 - VMOsAllow) / 4 - (1 - VMOsVersionAllow) / 4

    # 虚拟机性能评分
    performance_score = 1 - (1 - CPU) / 4 - (1 - mem) / 4

    # 连接次数与成功率评分
    fail_rate = (VMLoginTotal - VMLoginSucceed) / (VMLoginTotal + EPS)
    connection_score = 1 - sigmoid((VMConnectionUser - 1) / 3) - fail_rate * sigmoid(VMLoginTotal - TAU)

    # 安全态势评分
    alert_score_VM = 1 - math.tanh(VMAlert / 10)

    return ProcessedVM(
        vm_id=vm_id,
        os_score=os_score,
        performance_score=performance_score,
        connection_score=connection_score,
        alert_score_VM=alert_score_VM
    )

