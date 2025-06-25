import re
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sales_rag_app'))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

def test_regex_extraction():
    """测试正则表达式提取逻辑"""
    
    print("=== 测试正则表达式提取逻辑 ===")
    
    # 测试数据
    test_data = [
        {
            "modelname": "AHP958",
            "cpu": "- AMD Zen4, Hawk Point HS Series, TDP: 45W\n  - Ryzen™ 5 8645HS (8C/16T, 5.2GHz/4.0GHz, TDP: 35W~54W)\n  - Ryzen™ 7 8845HS (8C/16T, 5.1GHz/3.8GHz, TDP: 35W~54W)\n  - Ryzen™ 9 8945HS (8C/16T, 5.0GHz/3.5GHz, TDP: 35W~54W)",
            "gpu": "- AMD Radeon™ RX7600M (P1), 8GB GDDR6, 90W, Smart Shift: 100W\n- AMD Radeon™ RX7600M XT (P2), 8GB GDDR6, 120W, Smart Shift: 130W",
            "memory": "- 2 × DDR5 SO-DIMM, up to 32GB DDR5 5600MHz (2 × 16GB)",
            "storage": "- 2 × M.2 2280 PCIe Gen4 (Lane 4) NVMe SSD, up to 8TB (2 × 1TB)",
            "battery": "- Type: Lithium-ion polymer battery\n- Capacity: 80.08 Wh, 15.4V / 5200mAh, 4S1P, Smart battery\n- Certifications: CE, FCC, CCC, CB, MSDS, UN38.3, Airflight transportation report\n- Estimated Life: 10 hours"
        },
        {
            "modelname": "AG958",
            "cpu": "- AMD Zen3+, Rembrandt H Series\n  * Ryzen™ 5 6600H (6C/12T, 4.5GHz/3.3GHz, TDP: 45W)\n  * Ryzen™ 7 6800H (8C/16T, 4.7GHz/3.2GHz, TDP: 45W)",
            "gpu": "- AMD Radeon™ RX6550M (E65), 8GB GDDR6, 90W\n- AMD Radeon™ RX6550M XT (E100), 8GB GDDR6, 90W",
            "memory": "- 2 × DDR5 SO-DIMM, up to 32GB DDR5 4800MHz (2 × 16GB)",
            "storage": "- 2 × M.2 2280 PCIe Gen4 (Lane 4) NVMe SSD, up to 8TB (2 × 1TB)",
            "battery": "- Type: Lithium-ion polymer battery\n- Capacity: 80.08 Wh, 15.4V / 5200mAh, 4S1P, Smart battery\n- Certifications: CE, FCC, CCC, CB, MSDS, UN38.3, Airflight transportation report\n- Estimated Life: 10 hours"
        }
    ]
    
    print("\n1. 测试CPU提取:")
    for model in test_data:
        cpu_data = model["cpu"]
        print(f"\n{model['modelname']} CPU数据:")
        print(cpu_data)
        
        # 测试不同的正则表达式
        patterns = [
            r"Ryzen™\s+\d+\s+\d+[A-Z]*[HS]*",
            r"Ryzen™\s+\d+\s+\d+[A-Z]*",
            r"Ryzen™\s+\d+\s+\d+"
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, cpu_data)
            print(f"  模式{i+1} '{pattern}': {matches}")
    
    print("\n2. 测试GPU提取:")
    for model in test_data:
        gpu_data = model["gpu"]
        print(f"\n{model['modelname']} GPU数据:")
        print(gpu_data)
        
        patterns = [
            r"AMD Radeon™\s+[A-Z0-9]+[A-Z]*",
            r"AMD Radeon™\s+[A-Z0-9]+",
            r"Radeon™\s+[A-Z0-9]+[A-Z]*"
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, gpu_data)
            print(f"  模式{i+1} '{pattern}': {matches}")
    
    print("\n3. 测试内存提取:")
    for model in test_data:
        memory_data = model["memory"]
        print(f"\n{model['modelname']} 内存数据:")
        print(memory_data)
        
        memory_match = re.search(r"DDR\d+", memory_data)
        print(f"  DDR匹配: {memory_match.group(0) if memory_match else 'N/A'}")
    
    print("\n4. 测试存储提取:")
    for model in test_data:
        storage_data = model["storage"]
        print(f"\n{model['modelname']} 存储数据:")
        print(storage_data)
        
        storage_match = re.search(r"M\.2.*?PCIe.*?NVMe", storage_data)
        print(f"  存储匹配: {storage_match.group(0) if storage_match else 'N/A'}")
    
    print("\n5. 测试电池提取:")
    for model in test_data:
        battery_data = model["battery"]
        print(f"\n{model['modelname']} 电池数据:")
        print(battery_data)
        
        battery_match = re.search(r"(\d+\.?\d*)\s*Wh", battery_data)
        print(f"  电池容量: {battery_match.group(1) + 'Wh' if battery_match else 'N/A'}")

def test_fallback_table_generation():
    """测试备用表格生成"""
    
    service = SalesAssistantService()
    
    print("\n=== 测试备用表格生成 ===")
    
    # 测试数据
    context_data = [
        {
            "modelname": "AHP958",
            "cpu": "- AMD Zen4, Hawk Point HS Series, TDP: 45W\n  - Ryzen™ 5 8645HS (8C/16T, 5.2GHz/4.0GHz, TDP: 35W~54W)\n  - Ryzen™ 7 8845HS (8C/16T, 5.1GHz/3.8GHz, TDP: 35W~54W)\n  - Ryzen™ 9 8945HS (8C/16T, 5.0GHz/3.5GHz, TDP: 35W~54W)",
            "gpu": "- AMD Radeon™ RX7600M (P1), 8GB GDDR6, 90W, Smart Shift: 100W\n- AMD Radeon™ RX7600M XT (P2), 8GB GDDR6, 120W, Smart Shift: 130W",
            "memory": "- 2 × DDR5 SO-DIMM, up to 32GB DDR5 5600MHz (2 × 16GB)",
            "storage": "- 2 × M.2 2280 PCIe Gen4 (Lane 4) NVMe SSD, up to 8TB (2 × 1TB)",
            "battery": "- Type: Lithium-ion polymer battery\n- Capacity: 80.08 Wh, 15.4V / 5200mAh, 4S1P, Smart battery\n- Certifications: CE, FCC, CCC, CB, MSDS, UN38.3, Airflight transportation report\n- Estimated Life: 10 hours"
        },
        {
            "modelname": "AG958",
            "cpu": "- AMD Zen3+, Rembrandt H Series\n  * Ryzen™ 5 6600H (6C/12T, 4.5GHz/3.3GHz, TDP: 45W)\n  * Ryzen™ 7 6800H (8C/16T, 4.7GHz/3.2GHz, TDP: 45W)",
            "gpu": "- AMD Radeon™ RX6550M (E65), 8GB GDDR6, 90W\n- AMD Radeon™ RX6550M XT (E100), 8GB GDDR6, 90W",
            "memory": "- 2 × DDR5 SO-DIMM, up to 32GB DDR5 4800MHz (2 × 16GB)",
            "storage": "- 2 × M.2 2280 PCIe Gen4 (Lane 4) NVMe SSD, up to 8TB (2 × 1TB)",
            "battery": "- Type: Lithium-ion polymer battery\n- Capacity: 80.08 Wh, 15.4V / 5200mAh, 4S1P, Smart battery\n- Certifications: CE, FCC, CCC, CB, MSDS, UN38.3, Airflight transportation report\n- Estimated Life: 10 hours"
        }
    ]
    
    target_modelnames = ["AHP958", "AG958"]
    
    # 测试不同类型的查询
    queries = [
        "比较AHP958和AG958的CPU性能",
        "比较AHP958和AG958的GPU性能",
        "比较AHP958和AG958的规格"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        table = service._generate_fallback_table(context_data, target_modelnames, query)
        print("生成的表格:")
        for row in table:
            print(f"  {row}")

if __name__ == "__main__":
    test_regex_extraction()
    test_fallback_table_generation() 