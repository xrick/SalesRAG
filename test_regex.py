import re

def test_model_name_detection():
    test_str = 'Yes, the APX819 FP7R2 supports dual-channel RAM configuration as it has two separate SO-DIMM slots.'
    target_model = 'APX819: FP7R2'
    potential_models = []
    
    print(f'Target model: {target_model}')
    print(f'Contains colon: {":" in target_model}')
    
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
    
    # 检查是否包含目标模型的变体
    target_variants = [target_model, target_model.replace(":", "")]
    print(f'Target variants: {target_variants}')
    
    for variant in target_variants:
        if variant in potential_models:
            print(f'Found valid variant: {variant}')
            return True
    
    print('No valid variant found')
    return False

if __name__ == "__main__":
    test_model_name_detection() 