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

    def __repr__(self):
        return (f"RawUser(user_id={self.user_id}, userType={self.userType}, "
                f"thresholdDelta={self.thresholdDelta}, "
                f"loginTotal={self.loginTotal}, loginSucceed={self.loginSucceed}, "
                f"ifLoginTimeOK={self.ifLoginTimeOK}, "
                f"loginTimeBias={self.loginTimeBias}, loginTimeDiff={self.loginTimeDiff}, "
                f"ifIpAllow={self.ifIpAllow}, ifAreaAllow={self.ifAreaAllow})")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "userType": self.userType,
            "thresholdDelta": self.thresholdDelta,
            "loginTotal": self.loginTotal,
            "loginSucceed": self.loginSucceed,
            "ifLoginTimeOK": self.ifLoginTimeOK,
            "loginTimeBias": self.loginTimeBias,
            "loginTimeDiff": self.loginTimeDiff,
            "ifIpAllow": self.ifIpAllow,
            "ifAreaAllow": self.ifAreaAllow
        }

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

    def __repr__(self):
        return (f"ProcessedUser(user_id={self.user_id}, "
                f"userType={self.userType}, login_score={self.login_score:.3f}, "
                f"time_score={self.time_score:.3f}, env_score={self.env_score:.3f}, "
                f"trust_score={self.trust_score})")
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "userType": self.userType,
            "thresholdDelta": self.thresholdDelta,
            "loginTimeDiff": self.loginTimeDiff,
            "login_score": self.login_score,
            "time_score": self.time_score,
            "env_score": self.env_score,
            "trust_score": self.trust_score
        }