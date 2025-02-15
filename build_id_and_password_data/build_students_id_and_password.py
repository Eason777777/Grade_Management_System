import pandas as pd
import random

# 設定隨機種子以便重現相同的隨機結果
random.seed(42)

# 讀取學院和科系資料
df_departments = pd.read_csv(r'build_id_and_password_data\department_codes.csv', encoding='utf-8-sig')

# 建立學院代碼到學系代碼的映射
college_to_departments = df_departments.groupby('College Code')['Department Code'].apply(list).to_dict()

# 定義學院代碼
colleges = list(college_to_departments.keys())

# 生成學生學號
def generate_student_id(degree, admission_year, college, department, class_number, seat_number):
    """生成學生學號"""
    return f'{degree}{admission_year}{department}{class_number}{seat_number}{college}'

# 生成學生資料
students_data = []

for college in colleges:
    departments = college_to_departments[college]
    for department in departments:
        num_students = random.randint(40, 50)  # 每個學系生成40到50個學生
        for seat_number in range(1, num_students + 1):
            degree = '4'
            admission_year = random.randint(10, 12)
            class_number = f'{random.randint(0, 2)}'
            seat_number_str = f'{seat_number:02d}'  # 座號從01開始
            
            student_id = generate_student_id(degree, admission_year, college, department, class_number, seat_number_str)
            name = f'學生{len(students_data) + 1}'  # 模擬學生姓名
            password = f'{random.randint(1000, 9999)}'  # 模擬密碼
            students_data.append([student_id, password, name])

# 創建DataFrame
df = pd.DataFrame(students_data, columns=['學號', '密碼', '姓名'])

# 保存到CSV文件
df.to_csv(r'build_id_and_password_data\student_data.csv', index=False, encoding='utf-8-sig')

print("學生資料已保存到 'student_data.csv'")
