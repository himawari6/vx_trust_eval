import json

def fix_json_file(input_path, output_path):
    # 读取原始文件内容
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # 分割成独立的对象
    objects = []
    brace_count = 0
    current_obj = []
    
    # 解析大括号匹配
    for char in content:
        if char == '{':
            brace_count += 1
            current_obj.append(char)
        elif char == '}':
            brace_count -= 1
            current_obj.append(char)
            if brace_count == 0:
                objects.append(''.join(current_obj))
                current_obj = []
        elif brace_count > 0:
            current_obj.append(char)
    
    # 验证是否成对
    if len(objects) % 2 != 0:
        print("警告：对象数量不是偶数，可能存在不完整的组")
    
    # 构建结构化JSON
    structured_data = []
    for i in range(0, len(objects), 2):
        try:
            input_data = json.loads(objects[i])
            output_data = json.loads(objects[i+1])
            
            # 验证消息类型
            if input_data.get('message') == '原始数据' and output_data.get('message') == '评估结果':
                structured_data.append({
                    "input": input_data,
                    "output": output_data
                })
        except (json.JSONDecodeError, IndexError) as e:
            print(f"解析错误: {e}")
    
    # 保存修复后的文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=4)

# 使用示例
fix_json_file('..\\log\\测试数据.json', '..\\samples\\sample_01.json')