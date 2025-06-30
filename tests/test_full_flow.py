import json
import sys
import os
import asyncio

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sales_rag_app'))

from sales_rag_app.libs.services.sales_assistant.service import SalesAssistantService

async def test_full_flow():
    """测试完整的请求流程"""
    
    # 创建服务实例
    service = SalesAssistantService()
    
    # 测试查询
    query = "APX819: FP7R2 dual channel RAM"
    
    print(f"=== 测试查询: {query} ===")
    
    # 模拟异步生成器
    async def mock_chat_stream():
        async for response in service.chat_stream(query):
            print(f"收到响应: {response}")
            # 解析响应
            if response.startswith('data: '):
                json_str = response[6:]  # 移除 'data: ' 前缀
                try:
                    data = json.loads(json_str)
                    print(f"解析后的数据:")
                    print(f"  answer_summary: {data.get('answer_summary', '')}")
                    print(f"  comparison_table: {data.get('comparison_table', '')}")
                    print(f"  beautiful_table: {data.get('beautiful_table', '')}")
                    return data
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    return None
    
    try:
        result = await mock_chat_stream()
        if result:
            print("\n=== 最终结果 ===")
            print(f"answer_summary: {result.get('answer_summary', '')}")
            print(f"comparison_table: {result.get('comparison_table', '')}")
            print(f"beautiful_table: {result.get('beautiful_table', '')}")
        else:
            print("没有收到有效响应")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_flow()) 