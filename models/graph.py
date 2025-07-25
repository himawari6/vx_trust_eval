from policy import generate_action

class Connection:
    """
    单次连接对象，存储用户-终端-虚拟机间的一次具体连接信息
    """
    def __init__(self, connectionId, connectStart, connectEnd, onlineTime, user_id, terminal_id, vm_id, alertNum):
        self.connectionId = connectionId
        self.connectStart = connectStart
        self.connectEnd = connectEnd
        self.onlineTime = onlineTime  # 持续时长（秒）
        self.user_id = user_id
        self.terminal_id = terminal_id
        self.vm_id = vm_id
        self.alertNum = alertNum

    def __repr__(self):
        return (f"Connection(id={self.connectionId}, "
                f"start={self.connectStart}, end={self.connectEnd}, "
                f"onlineTime={self.onlineTime}, "
                f"user={self.user_id}, terminal={self.terminal_id}, vm={self.vm_id}, "
                f"alertNum={self.alertNum})")
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "terminal_id": self.terminal_id,
            "vm_id": self.vm_id,
            "connectionId": self.connectionId,
            "connectStart": str(self.connectStart),
            "connectEnd": str(self.connectEnd),
            "onlineTime": self.onlineTime,
            "alertNum": self.alertNum
        }

class Graph:
    """
    信任传播图，N×M结构的连接矩阵
    """
    def __init__(self):
        self.users = {}      # user_id -> ProcessedUser
        self.terminals = {}  # terminal_id -> ProcessedTerminal
        self.vms = {}        # vm_id -> ProcessedVM

        # 每个用户的连接矩阵：user_id -> { terminal_id: { vm_id: 累计在线时长 } }
        self.connection_time = {}

    def add_user(self, user):
        self.users[user.user_id] = user
        if user.user_id not in self.connection_time:
            self.connection_time[user.user_id] = {}

    def add_terminal(self, terminal):
        self.terminals[terminal.terminal_id] = terminal

    def add_vm(self, vm):
        self.vms[vm.vm_id] = vm

    def add_connection(self, user_id, terminal_id, vm_id, online_time):
        """
        累计连接时长
        """
        if user_id not in self.connection_time:
            self.connection_time[user_id] = {}
        if terminal_id not in self.connection_time[user_id]:
            self.connection_time[user_id][terminal_id] = {}
        self.connection_time[user_id][terminal_id][vm_id] = (
            self.connection_time[user_id][terminal_id].get(vm_id, 0) + online_time
        )

    def get_terminal_vms_time(self, user_id, terminal_id):
        """
        获取某用户下，指定终端与各虚拟机的累计连接时间
        """
        # 返回字典，键为虚拟机号m，值为k号终端连接m号虚拟机的时间w(k,m)，维数1*M，M为虚拟机数量，共M个键值对
        return self.connection_time.get(user_id, {}).get(terminal_id, {})

    def get_user_terminals_time(self, user_id):
        """
        获取某用户下，各终端的总连接时间
        """
        terminals = self.connection_time.get(user_id, {})
        terminal_total_time = {
            terminal_id: sum(vm_times.values())
            for terminal_id, vm_times in terminals.items()
        }
        # 返回字典，键为终端号k，值为k号终端连接虚拟机的总时间C(k)，维数1*N，N为终端数量，共N个键值对
        return terminal_total_time

    def to_dict(self):
        return {
            "users": [user_id for user_id, ProcessedUser in self.users.items()],
            "terminals": [terminal_id for terminal_id, ProcessedTerminal in self.terminals.items()],
            "vms": [vm_id for vm_id, ProcessedVM in self.vms.items()],
            "connection_time": self.connection_time
        }
    
    def extract_user_vm_ids_map(self) -> dict[str, set[str]]:
        user_vm = {}
        for user_id, term_dict in self.connection_time.items():
            vm_ids = set()
            for vm_dict in term_dict.values():
                vm_ids.update(vm_dict.keys())  # 批量添加虚拟机ID
            user_vm[user_id] = vm_ids
        return user_vm
    
    def extract_user_action_map(self):
        user_action = {}
        for user_id, user in self.users.items():
            user_action[user_id] = generate_action(user)
        return user_action