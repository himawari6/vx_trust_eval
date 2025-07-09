# 第一组：原始数据结构
class RawVM:
    def __init__(self, vm_id, VMOsAllow, VMOsVersionAllow, CPU, mem,
                 VMConnectionUser, VMLoginTotal, VMLoginSucceed, VMAlert):
        self.vm_id = vm_id  # 虚拟机唯一标识
        self.VMOsAllow = VMOsAllow  # 是否符合系统类型规则
        self.VMOsVersionAllow = VMOsVersionAllow  # 是否符合版本规则
        self.CPU = CPU  # CPU利用率特征
        self.mem = mem  # 内存利用率特征
        self.VMConnectionUser = VMConnectionUser  # 连接的用户数量
        self.VMLoginTotal = VMLoginTotal  # 登录次数
        self.VMLoginSucceed = VMLoginSucceed  # 登录成功次数
        self.VMAlert = VMAlert  # 安全告警数量


# 第二组：预处理后特征数据结构
class ProcessedVM:
    def __init__(self, vm_id, os_score, performance_score, connection_score, alert_score_VM):
        self.vm_id = vm_id

        # 预处理后的特征
        self.os_score = os_score  # w6权重特征
        self.performance_score = performance_score # w7权重特征
        self.connection_score = connection_score  # w8权重特征
        self.alert_score_VM = alert_score_VM  # w9权重特征

        self.trust_score = None  # 信任值，后续计算得到
