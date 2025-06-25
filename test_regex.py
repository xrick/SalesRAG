import re

def test_model_name_detection():
    # 使用实际的LLM回答
    test_str = 'Yes, the APX819 FP7R2 supports dual-channel RAM configuration. This is possible due to the presence of two SO-DIMM slots in the system, each capable of supporting a single channel of memory.'
    target_model = 'APX819: FP7R2'
    potential_models = []
    
    print(f'Target model: {target_model}')
    print(f'Contains colon: {":" in target_model}')
    
    # 生成目标模型的变体
    target_variants = [target_model, target_model.replace(":", "")]
    print(f'Target variants: {target_variants}')
    
    # 首先检查是否包含目标模型名称的变体
    has_valid_model = False
    for model_variant in target_variants:
        if model_variant in test_str:
            has_valid_model = True
            print(f'Found valid variant: {model_variant}')
            break
    
    if not has_valid_model:
        print('No direct match found, using regex...')
        
        if ":" in target_model:
            # 如果目标模型包含冒号，使用匹配冒号格式的正则表达式
            pattern = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s*:\s*[A-Z]+\d+[A-Z]*)'
            matches = re.findall(pattern, test_str)
            potential_models.extend(matches)
            print(f'With colon pattern matches: {matches}')
            
            # 也匹配没有冒号的版本 - 修复正则表达式以匹配完整的模型名称
            pattern_no_colon = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s+[A-Z]+\d+[A-Z]*\d*)'
            matches_no_colon = re.findall(pattern_no_colon, test_str)
            potential_models.extend(matches_no_colon)
            print(f'Without colon pattern matches: {matches_no_colon}')
        else:
            # 如果目标模型不包含冒号，使用简单格式的正则表达式
            pattern = r'[A-Z]{2,3}\d{3}(?:-[A-Z]+)?'
            matches = re.findall(pattern, test_str)
            potential_models.extend(matches)
            print(f'Simple pattern matches: {matches}')
        
        # 去重
        potential_models = list(set(potential_models))
        print(f'All potential models: {potential_models}')
        
        for potential_model in potential_models:
            # 检查是否是目标模型的变体
            is_valid_variant = False
            for model_variant in target_variants:
                if potential_model == model_variant:
                    is_valid_variant = True
                    print(f'Found valid variant via regex: {potential_model} -> {model_variant}')
                    break
            
            if is_valid_variant:
                return True
        
        print('No valid variant found via regex')
        return False
    
    return True

if __name__ == "__main__":
    result = test_model_name_detection()
    print(f'Final result: {result}') 