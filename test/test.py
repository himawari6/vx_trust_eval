import json
from preprocess import aggregate_alerts, preprocess_user, preprocess_terminal, preprocess_vm
from trust_algorithm import build_graph, trust_propagation
from policy import generate_action

from models.user import RawUser
from models.terminal import RawTerminal
from models.vm import RawVM
from models.graph import Connection

def load_samples(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 预期 data 是一个样本数组
    if not isinstance(data, list):
        raise ValueError("样本文件的顶层必须是数组(list)。")
    return data

def read_raw_user(raw_user_dict):
    return RawUser(
        record_id=raw_user_dict["record_id"],
        user_id=raw_user_dict["user_id"],
        userType=raw_user_dict.get("userType"),
        thresholdDelta=raw_user_dict.get("thresholdDelta"),
        loginTotal=raw_user_dict.get("loginTotal"),
        loginSucceed=raw_user_dict.get("loginSucceed"),
        ifLoginTimeOK=raw_user_dict.get("ifLoginTimeOK"),
        loginTimeBias=raw_user_dict.get("loginTimeBias"),
        loginTimeDiff=raw_user_dict.get("loginTimeDiff"),
        ifIpAllow=raw_user_dict.get("ifIpAllow"),
        ifAreaAllow=raw_user_dict.get("ifAreaAllow"),
    )


def read_raw_terminal(raw_terminal_dict):
    return RawTerminal(
        terminal_id=raw_terminal_dict["terminal_id"],
        terminalType=raw_terminal_dict.get("terminalType"),
        userDiff=raw_terminal_dict.get("userDiff"),
        terminalAlert=raw_terminal_dict.get("terminalAlert", 0)
    )


def read_raw_vm(raw_vm_dict):
    return RawVM(
        vm_id=raw_vm_dict["vm_id"],
        VMOsAllow=raw_vm_dict.get("VMOsAllow"),
        VMOsVersionAllow=raw_vm_dict.get("VMOsVersionAllow"),
        CPU=raw_vm_dict.get("CPU"),
        mem=raw_vm_dict.get("mem"),
        VMConnectionUser=raw_vm_dict.get("VMConnectionUser"),
        VMLoginTotal=raw_vm_dict.get("VMLoginTotal"),
        VMLoginSucceed=raw_vm_dict.get("VMLoginSucceed"),
        VMAlert=raw_vm_dict.get("VMAlert", 0)
    )


def read_connection(connection_dict):
    return Connection(
        connectStart=connection_dict.get("connectStart"),
        connectEnd=connection_dict.get("connectEnd"),
        onlineTime=connection_dict.get("onlineTime"),
        user_id=connection_dict.get("user_id"),
        terminal_id=connection_dict.get("terminal_id"),
        vm_id=connection_dict.get("vm_id"),
        connectionId=connection_dict.get("connectionId"),
        alertNum=connection_dict.get("alertNum")
    )

def extract_input_data_from_sample(sample):
    raw = sample["input"]
    raw_users = [read_raw_user(u) for u in raw["raw_users"]]
    raw_terminals = [read_raw_terminal(t) for t in raw["raw_terminals"]]
    raw_vms = [read_raw_vm(vm) for vm in raw["raw_vms"]]
    connections = [read_connection(c) for c in raw["connections"]]
    return raw_users, raw_terminals, raw_vms, connections

def extract_output_data_from_sample(sample):
    raw_results = sample["output"]['results']
    ground_truth = []
    for user_id, raw_result in raw_results.items():
        ground_truth.append({
            "user_id": user_id,
            "label": raw_result['label']
        })
    
    return ground_truth



def generate_policy_signal(processed_users):
    result = []
    for user in processed_users:
        result.append({
            "user_id": user.user_id,
            "trust": user.trust_score,
            "action": generate_action(user)
        })
    return result

def test_evaluate_sample(sample):
    #读入input
    raw_users, raw_terminals, raw_vms, connections = extract_input_data_from_sample(sample)
    #读入output(gt)
    ground_truth = extract_output_data_from_sample(sample)

    aggregate_alerts(connections, raw_terminals, raw_vms)
    users = [preprocess_user(u) for u in raw_users]
    terminals = [preprocess_terminal(t) for t in raw_terminals]
    vms = [preprocess_vm(vm) for vm in raw_vms]

    graph = build_graph(users, terminals, vms, connections)
    trust_propagation(graph)

    results = generate_policy_signal(users)

    total_cnt = 0
    correct_cnt = 0
    for i in range(len(results)):
        total_cnt = total_cnt + 1
        print(results[i]['trust'], results[i]['action'], ground_truth[i]['label'])
        if results[i]['action'] == ground_truth[i]['label']:
            correct_cnt = correct_cnt + 1
    
    return {"total": total_cnt, "correct": correct_cnt}

def test_evaluate_dataset(samples):
    test_result = {"total": 0, "correct": 0, "accuracy": 0}
    for sample in samples:
        result = test_evaluate_sample(sample)
        test_result["total"] += result["total"]
        test_result["correct"] += result["correct"]
    test_result["accuracy"] = test_result["correct"] / test_result["total"]
    return test_result

if __name__ == '__main__':
    samples = load_samples('samples\\sample_01.json')
    print(test_evaluate_dataset(samples))

    
