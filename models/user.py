# 第一组：原始数据结构
class RawUser:
    def __init__(self, user_id, userType, thresholdDelta, loginTotal, loginSucceed,
                 ifLoginTimeOK, loginTimeBias, loginTimeDiff, 
                 ifIpAllow, ifAreaAllow):
        self.user_id = user_id  # 用户唯一标识
        self.userType = userType  # 管理员：1，普通用户：0
        self.thresholdDelta = thresholdDelta  # 信任阈值调整因子
        self.loginTotal = loginTotal  # 尝试登录次数
        self.loginSucceed = loginSucceed  # 登录成功次数
        self.ifLoginTimeOK = ifLoginTimeOK  # 是否异常时间登录
        self.loginTimeBias = loginTimeBias  # 偏离习惯登录时间
        self.loginTimeDiff = loginTimeDiff  # 最近访问时间差（时间戳）
        self.ifIpAllow = ifIpAllow  # 是否允许网段登录
        self.ifAreaAllow = ifAreaAllow  # 是否允许地理位置登录


# 第二组：预处理后特征数据结构
class ProcessedUser:
    def __init__(self, user_id, userType, thresholdDelta, loginTimeDiff, 
                 login_score, time_score, env_score):
        self.user_id = user_id
        self.userType = userType
        self.thresholdDelta = thresholdDelta
        self.loginTimeDiff = loginTimeDiff

        # 预处理后的特征
        self.login_score = login_score  # w1权重特征
        self.time_score = time_score  # w2权重特征
        self.env_score = env_score  # w3权重特征

        self.trust_score = None  # 信任值，后续计算得到
