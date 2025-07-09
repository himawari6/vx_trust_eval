import math
from models.user import RawUser, ProcessedUser
from models.terminal import RawTerminal, ProcessedTerminal
from models.vm import RawVM, ProcessedVM
from utils import sigmoid
from config import EPS, TAU

def preprocess_user(raw_user: RawUser):
    """用户节点特征预处理"""
    loginTotal = raw_user.loginTotal
    loginSucceed = raw_user.loginSucceed

    # 登录次数与成功率评分
    fail_rate = (loginTotal - loginSucceed) / (loginTotal + EPS)
    login_score = 1 - fail_rate * sigmoid(loginTotal - TAU)

    # 登录时间评分
    part1 = 0.4 * (1 - (raw_user.ifLoginTimeOK + 1) / 2)
    part2 = 0.3 * (1 - sigmoid(abs(raw_user.loginTimeBias)))
    part3 = 0.3 * (1 - sigmoid(raw_user.loginTimeDiff / 43200))
    time_score = part1 + part2 + part3

    # 登录环境与网络地址评分
    env_score = 2 - (1 - raw_user.ifIpAllow) / 2 - (1 - raw_user.ifAreaAllow) / 2

    return ProcessedUser(
        user_id=raw_user.user_id,
        userType=raw_user.userType,
        thresholdDelta=raw_user.thresholdDelta,
        loginTimeDiff=raw_user.loginTimeDiff,
        login_score=login_score,
        time_score=time_score,
        env_score=env_score,
        continueTime=raw_user.continueTime
    )

def preprocess_terminal(raw_terminal: RawTerminal):
    """终端节点特征预处理"""
    # 基本信息评分
    basic_score = 2 - (raw_terminal.terminalType - 1) / 2 - (1 - raw_terminal.userDiff) / 2

    # 安全态势评分
    alert_score_terminal = 1 - math.tanh(raw_terminal.terminalAlert / 10)

    return ProcessedTerminal(
        terminal_id=raw_terminal.terminal_id,
        basic_score=basic_score,
        alert_score_terminal=alert_score_terminal
    )

def preprocess_vm(raw_vm: RawVM):
    """虚拟机节点特征预处理"""
    # 系统信息评分
    os_score = 2 - (1 - raw_vm.VMOsAllow) / 2 - (1 - raw_vm.VMOsVersionAllow) / 2

    # 虚拟机性能评分
    performance_score = 2 - (1 - raw_vm.CPU) / 2 - (1 - raw_vm.mem) / 2

    # 连接次数与成功率评分
    fail_rate = (raw_vm.VMLoginTotal - raw_vm.VMLoginSucceed) / (raw_vm.VMLoginTotal + EPS)
    connection_score = 1 - sigmoid((raw_vm.VMConnectionUser - 1) / 3) - fail_rate * sigmoid(raw_vm.VMLoginTotal - TAU)

    # 安全态势评分
    alert_score_VM = 1 - math.tanh(raw_vm.VMAlert / 10)

    return ProcessedVM(
        vm_id=raw_vm.vm_id,
        os_score=os_score,
        performance_score=performance_score,
        connection_score=connection_score,
        alert_score_VM=alert_score_VM
    )

