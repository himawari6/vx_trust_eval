import pymysql
from models.user import RawUser
from models.terminal import RawTerminal
from models.vm import RawVM
from models.graph import Connection
from config import DB_CONFIG


def get_all_data():
    """
    获取全量用户、终端、虚拟机、连接数据
    """
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 查询用户
        cursor.execute("SELECT * FROM user_feature")
        raw_users = [
            RawUser(
                row["userId"], row["userType"], row["threshold"], row["loginTotal"],
                row["loginSucceed"], row["ifLoginTimeOK"], row["LoginTimeBias"],
                row["LoginTimeDiff"].timestamp() if row["LoginTimeDiff"] else 0,
                row["ifIpAllow"], row["ifAreaAllow"]
            )
            for row in cursor.fetchall()
        ]

        # 查询终端
        cursor.execute("SELECT * FROM terminal_feature")
        raw_terminals = [
            RawTerminal(
                row["terminalId"], row["terminalType"], row["userDiff"], row["terminalAlert"]
            )
            for row in cursor.fetchall()
        ]

        # 查询虚拟机
        cursor.execute("SELECT * FROM vm_feature")
        raw_vms = [
            RawVM(
                row["resourceId"], row["VMOsAllow"], row["VMOsVersionAllow"], row["CPU"],
                row["mem"], row["VMConnectionUser"], row["VMLoginTotal"],
                row["VMLoginSucceed"], row["VMAlert"]
            )
            for row in cursor.fetchall()
        ]

        # 查询连接信息
        cursor.execute("SELECT * FROM connection")
        connections = [
            Connection(
                row["connectStart"], row["connectEnd"], row["onlineTime"],
                row["userId"], row["terminalId"], row["resourceId"], row["traceId"]
            )
            for row in cursor.fetchall()
        ]

    finally:
        cursor.close()
        conn.close()

    return raw_users, raw_terminals, raw_vms, connections

def get_specific_data(user_id, terminal_ids, vm_ids):
    """
    获取指定用户、终端、虚拟机及连接信息
    """
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 用户信息
        cursor.execute("SELECT * FROM user_feature WHERE userId = %s", (user_id,))
        row = cursor.fetchone()
        raw_users = []
        if row:
            raw_users.append(RawUser(
                row["userId"], row["userType"], row["threshold"], row["loginTotal"],
                row["loginSucceed"], row["ifLoginTimeOK"], row["LoginTimeBias"],
                row["LoginTimeDiff"].timestamp() if row["LoginTimeDiff"] else 0,
                row["ifIpAllow"], row["ifAreaAllow"]
            ))

        # 终端信息
        format_str = ",".join(["%s"] * len(terminal_ids))
        cursor.execute(f"SELECT * FROM terminal_feature WHERE terminalId IN ({format_str})", terminal_ids)
        raw_terminals = [
            RawTerminal(
                row["terminalId"], row["terminalType"], row["userDiff"], row["terminalAlert"]
            )
            for row in cursor.fetchall()
        ]

        # 虚拟机信息
        format_str = ",".join(["%s"] * len(vm_ids))
        cursor.execute(f"SELECT * FROM vm_feature WHERE resourceId IN ({format_str})", vm_ids)
        raw_vms = [
            RawVM(
                row["resourceId"], row["VMOsAllow"], row["VMOsVersionAllow"], row["CPU"],
                row["mem"], row["VMConnectionUser"], row["VMLoginTotal"],
                row["VMLoginSucceed"], row["VMAlert"]
            )
            for row in cursor.fetchall()
        ]

        # 连接信息
        cursor.execute("""
            SELECT * FROM connection
            WHERE userId = %s AND terminalId IN ({}) AND resourceId IN ({})
        """.format(
            ",".join(["%s"] * len(terminal_ids)),
            ",".join(["%s"] * len(vm_ids))
        ), (user_id, *terminal_ids, *vm_ids))

        connections = [
            Connection(
                row["connectStart"], row["connectEnd"], row["onlineTime"],
                row["userId"], row["terminalId"], row["resourceId"], row["traceId"]
            )
            for row in cursor.fetchall()
        ]

    finally:
        cursor.close()
        conn.close()

    return raw_users, raw_terminals, raw_vms, connections