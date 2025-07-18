from flask import Flask, request, make_response
from flask_cors import CORS
import os
import json
import pexpect

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route("/api/v1/trust/trigger", methods=["POST"])
def send_pcap():
    # default return
    return_dict = {'return_code': '200', 'return_info': '处理成功'}
    # whether args are empty
    if request.get_json() is None:
        return_dict['return_code'] = '400'
        return_dict['return_info'] = '请求参数为空'
        return json.dumps(return_dict, ensure_ascii=False)

    # 获取传入的参数
    args = request.get_json()
    filename = args.get('filename')

    command = "sudo tcpreplay-edit -i ens45f0 --mtu-trunc 9600 " + "/home/chenqian/TrafficDetection/pcap/"+filename
    
    output = os.popen(command).read()
    return_dict['return_info'] = output
    return json.dumps(return_dict, ensure_ascii=False)

@app.route("/send_pcap", methods=["GET"])
def display_pcap():
    command = "ls /home/chenqian/TrafficDetection/pcap"
    output = os.popen(command).read().split("\n")[:-1]
    return_dict = {'return_code': '200', 'return_info': output}
    return json.dumps(return_dict, ensure_ascii=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)