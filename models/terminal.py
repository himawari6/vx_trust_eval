# 第一组：原始数据结构
class RawTerminal:
    def __init__(self, terminal_id, terminalType, userDiff, terminalAlert):
        self.terminal_id = terminal_id  # 终端唯一标识
        self.terminalType = terminalType  # 终端类型：1、2、3
        self.userDiff = userDiff  # 上次登录用户是否相同
        self.terminalAlert = terminalAlert  # 观测时间窗口内告警数量

    def __repr__(self):
        return (f"RawTerminal(terminal_id={self.terminal_id}, terminalType={self.terminalType}, "
                f"userDiff={self.userDiff}, terminalAlert={self.terminalAlert})")

# 第二组：预处理后特征数据结构
class ProcessedTerminal:
    def __init__(self, terminal_id, basic_score, alert_score_terminal):
        self.terminal_id = terminal_id

        # 预处理后的特征
        self.basic_score = basic_score  # w4权重特征
        self.alert_score_terminal = alert_score_terminal  # w5权重特征

        self.trust_score = None  # 信任值，后续计算得到

    def __repr__(self):
        return (f"ProcessedTerminal(terminal_id={self.terminal_id}, basic_score={self.basic_score:.3f}, "
                f"alert_score_terminal={self.alert_score_terminal:.3f}, trust_score={self.trust_score})")