import pandas as pd
import random

# 設定隨機種子以便重現相同的隨機結果
random.seed(42)

# 生成教師帳號和密碼
def generate_teacher_data(num_teachers):
    data = []
    for i in range(1, num_teachers + 1):
        # 生成帳號
        account_number = f'{i:03d}'
        # 生成隨機密碼
        password = f'{random.randint(1000, 9999)}'
        # 姓名格式
        name = f'教師{i}'
        # 將帳號、密碼和姓名加入資料
        data.append([account_number, password, name])
    return data

# 生成40個教師資料
teachers_data = generate_teacher_data(40)

# 創建DataFrame
df = pd.DataFrame(teachers_data, columns=['帳號', '密碼', '姓名'])

# 保存到CSV文件
df.to_csv(r'build_id_and_password_data\teacher_data.csv', index=False, encoding='utf-8-sig')

print("教師資料已保存到 'teacher_data.csv'")
