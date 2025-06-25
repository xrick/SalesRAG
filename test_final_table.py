def test_final_table_generation():
    """測試最終的表格生成功能"""
    
    # 模擬LLM回傳的dict of lists格式
    comparison_table = {
        "Model": ["AG958", "APX839"],
        "Battery Capacity (14\"/16\")": ["80Wh/99Wh", "80Wh/99Wh"],
        "Official Battery Life Test": [">10 Hours", ">10 Hours"]
    }
    
    model_names = ["AG958", "APX839"]
    
    print("=== 測試最終表格生成功能 ===\n")
    
    print(f"原始 comparison_table 類型: {type(comparison_table)}")
    print(f"原始 comparison_table 內容: {comparison_table}")
    print(f"原始 model_names: {model_names}")
    
    # 模擬轉換邏輯
    if isinstance(comparison_table, dict):
        print("檢測到 dict of lists 格式，開始轉換...")
        
        # 檢查是否有明確的項目欄位
        feature_keys = ["項目", "feature", "Feature", "Model"]
        items = None
        feature_key = None
        
        for key in feature_keys:
            if key in comparison_table:
                items = comparison_table[key]
                feature_key = key
                break
        
        if items is None:
            # 如果沒有找到明確的項目欄位，使用第一個欄位作為項目
            first_key = list(comparison_table.keys())[0]
            items = comparison_table[first_key]
            feature_key = first_key
        
        # 取得所有型號（排除項目欄位）
        available_models = [k for k in comparison_table.keys() if k != feature_key]
        
        # 如果沒有找到模型名稱，使用傳入的model_names
        if not available_models:
            available_models = model_names
        
        print(f"找到的項目欄位: {feature_key}")
        print(f"找到的項目: {items}")
        print(f"找到的模型: {available_models}")
        
        # 轉換
        new_table = []
        for idx, item in enumerate(items):
            row = {"feature": item}
            for model in available_models:
                values = comparison_table[model]
                row[model] = values[idx] if idx < len(values) else "N/A"
            new_table.append(row)
        comparison_table = new_table
        model_names = available_models  # 更新model_names
        
        print(f"轉換後的表格: {comparison_table}")
        print(f"更新後的模型名稱: {model_names}")

    # 確保 comparison_table 是列表格式
    if not isinstance(comparison_table, list):
        print(f"comparison_table 不是列表格式: {type(comparison_table)}")
        return

    # 生成表格
    header = "| **規格項目** |"
    separator = "| --- |"
    for name in model_names:
        header += f" **{name}** |"
        separator += " --- |"
    
    rows = []
    for row in comparison_table:
        if not isinstance(row, dict):
            print(f"表格行不是字典格式: {type(row)}")
            continue
            
        feature = row.get("feature", "N/A")
        row_str = f"| **{feature}** |"
        for model_name in model_names:
            value = row.get(model_name, "N/A")
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            row_str += f" {value_str} |"
        rows.append(row_str)
    
    table_lines = [header, separator] + rows
    result = "\n".join(table_lines)
    
    print(f"\n生成的表格:\n{result}")

if __name__ == "__main__":
    test_final_table_generation() 