import pymysql
from models.user import RawUser
from models.terminal import RawTerminal
from models.vm import RawVM
from models.graph import Connection
from config import DB_CONFIG


def get_all_data():
    """
    获取全量用户、终端、虚拟机、连接数据，仅保留每个实体的最新记录
    """
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 用户：保留每个 userId 的最新记录
        cursor.execute("""
            SELECT * FROM user_feature uf
            WHERE uf.id = (
                SELECT MAX(id) FROM user_feature WHERE userId = uf.userId
            )
        """)
        raw_users = [
            RawUser(
                user_id=row["userId"], 
                userType=row.get("userType"), 
                thresholdDelta=row.get("threshold"), 
                loginTotal=row.get("loginTotal"),
                loginSucceed=row.get("loginSucceed"), 
                ifLoginTimeOK=row.get("ifLoginTimeOK"), 
                loginTimeBias=row.get("LoginTimeBias"),
                loginTimeDiff=row.get("LoginTimeDiff"), 
                ifIpAllow=row.get("ifIpAllow"), 
                ifAreaAllow=row.get("ifAreaAllow")
            )
            for row in cursor.fetchall()
        ]

        # 终端：保留每个 terminalId 的最新记录
        cursor.execute("""
            SELECT * FROM terminal_feature tf
            WHERE tf.id = (
                SELECT MAX(id) FROM terminal_feature WHERE terminalId = tf.terminalId
            )
        """)
        raw_terminals = [
            RawTerminal(
                terminal_id=row["terminalId"], 
                terminalType=row.get("terminalType"), 
                userDiff=row.get("userDiff"), 
                terminalAlert=0  # 告警数先设为0
            )
            for row in cursor.fetchall()
        ]

        # 虚拟机：保留每个 resourceId 的最新记录
        cursor.execute("""
            SELECT * FROM vm_feature vf
            WHERE vf.id = (
                SELECT MAX(id) FROM vm_feature WHERE resourceId = vf.resourceId
            )
        """)
        raw_vms = [
            RawVM(
                row["resourceId"], row.get("VMOsAllow"), row.get("VMOsVersionAllow"), row.get("CPU"),
                row.get("mem"), row.get("VMConnectionUser"), row.get("VMLoginTotal"),
                row.get("VMLoginSucceed"), 0  # 告警数先设为0
            )
            for row in cursor.fetchall()
        ]

        # 所有连接记录
        cursor.execute("""
            SELECT * FROM connection
            WHERE state = '在线' OR TIMESTAMPDIFF(MINUTE, connectionEnd, NOW()) BETWEEN 0 AND 5""")
        connections = [
            Connection(
                row.get("connectionId"),
                row.get("connectStart"), row.get("connectEnd"), row.get("onlineTime"),
                row.get("userId"), row.get("terminalId"), row.get("resourceId"), 
                row.get("alert")  # JSON 字段
            )
            for row in cursor.fetchall()
        ]

    finally:
        cursor.close()
        conn.close()

    return raw_users, raw_terminals, raw_vms, connections


def get_specific_data(user_id, terminal_ids, vm_ids):
    """
    获取指定用户、终端、虚拟机及连接信息，仅保留这些实体的最新记录
    """
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 用户
        cursor.execute("""
            SELECT * FROM user_feature
            WHERE userId = %s
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        raw_users = []
        if row:
            raw_users.append(RawUser(
                row["userId"], row.get("userType"), row.get("threshold"), row.get("loginTotal"),
                row.get("loginSucceed"), row.get("ifLoginTimeOK"), row.get("LoginTimeBias"),
                row.get("LoginTimeDiff"), row.get("ifIpAllow"), row.get("ifAreaAllow")
            ))

        # 终端
        raw_terminals = []
        for tid in terminal_ids:
            cursor.execute("""
                SELECT * FROM terminal_feature
                WHERE terminalId = %s
                ORDER BY id DESC LIMIT 1
            """, (tid,))
            row = cursor.fetchone()
            if row:
                raw_terminals.append(RawTerminal(
                    row["terminalId"], row.get("terminalType"), row.get("userDiff"), 0
                ))

        # 虚拟机
        raw_vms = []
        for vid in vm_ids:
            cursor.execute("""
                SELECT * FROM vm_feature
                WHERE resourceId = %s
                ORDER BY id DESC LIMIT 1
            """, (vid,))
            row = cursor.fetchone()
            if row:
                raw_vms.append(RawVM(
                    row["resourceId"], row.get("VMOsAllow"), row.get("VMOsVersionAllow"), row.get("CPU"),
                    row.get("mem"), row.get("VMConnectionUser"), row.get("VMLoginTotal"),
                    row.get("VMLoginSucceed"), 0
                ))

        # 连接
        cursor.execute("""
            SELECT * FROM connection
            WHERE userId = %s AND terminalId IN ({}) AND resourceId IN ({})
        """.format(
            ",".join(["%s"] * len(terminal_ids)),
            ",".join(["%s"] * len(vm_ids))
        ), (user_id, *terminal_ids, *vm_ids))

        connections = [
            Connection(
                row.get("connectStart"), row.get("connectEnd"), row.get("onlineTime"),
                row.get("userId"), row.get("terminalId"), row.get("resourceId"), row.get("sessionId"),
                row.get("alert")
            )
            for row in cursor.fetchall()
        ]

    finally:
        cursor.close()
        conn.close()

    return raw_users, raw_terminals, raw_vms, connections
