import pandas as pd
import random
import numpy as np
import os

random.seed(42)


def grade_to_GPA(grade):
    if grade >= 90:
        return 4.3
    elif grade >= 85:
        return 4.0
    elif grade >= 80:
        return 3.7
    elif grade >= 77:
        return 3.3
    elif grade >= 73:
        return 3.0
    elif grade >= 70:
        return 2.7
    elif grade >= 67:
        return 2.4
    elif grade >= 63:
        return 2.0
    elif grade >= 60:
        return 1.7
    elif grade >= 50:
        return 1.0
    else:
        return 0

# 讀取學生資料


def load_student_data():
    df = pd.read_csv(r'build_id_and_password_data\student_data.csv',
                     encoding='utf-8-sig', dtype={'學號': str, '密碼': str})
    return df

# 讀取教師資料


def load_teacher_data():
    df = pd.read_csv(r'build_id_and_password_data\teacher_data.csv',
                     encoding='utf-8-sig', dtype={'帳號': str})
    return df

# 根據指定數量隨機選取學生


def select_random_students(df, num_students, random_state=None):
    return df.sample(n=num_students, replace=False, random_state=random_state)

# 生成課程資料並返回教師與學生資料


def create_course_data(course_code, course_name, credits, teacher, students_df):
    students_df['課程代碼'] = course_code
    students_df['課程名稱'] = course_name
    students_df['學分'] = credits
    students_df['教師'] = teacher
    np.random.seed(42)
    # 生成隨機分數（0到100）
    students_df['期中考'] = np.random.randint(0, 101, size=len(students_df))
    students_df['期末考'] = np.random.randint(0, 101, size=len(students_df))
    students_df['平時成績'] = np.random.randint(0, 101, size=len(students_df))

    # 選擇欄位並重新排序
    course_df = students_df[['學號', '姓名', '課程代碼',
                             '課程名稱', '學分', '教師', '期中考', '期末考', '平時成績']]

    # 返回教師與學生的資料
    return teacher, course_df

# 從文件中讀取課程代碼、名稱和學分


def load_course_names_and_credits(filename):
    courses = []
    df = pd.read_csv(filename, encoding='utf8')
    for _, row in df.iterrows():
        course_code = row['課程代碼']
        course_name = row['課程名稱']
        credits = int(row['學分'])
        courses.append((course_code, course_name, credits))
    return courses

# 生成課程與教師的對應表


def create_courses_data(courses, teachers):
    courses_data = []
    teacher_count = len(teachers)
    for i, (course_code, course_name, credits) in enumerate(courses):
        teacher = teachers[i % teacher_count]  # 保證每位教師至少一門課程
        courses_data.append((course_code, course_name, credits, teacher))
    return courses_data

# 主程序


def main():
    # 讀取學生資料
    students_df = load_student_data()

    # 讀取教師資料
    teachers_df = load_teacher_data()
    teachers_list = teachers_df['姓名'].tolist()
    random.shuffle(teachers_list)  # 隨機排列教師

    # 讀取課程名稱和學分
    courses = load_course_names_and_credits(
        r'build_course_data\course_name.csv')

    # 創建課程與教師對應表
    courses_data = create_courses_data(courses, teachers_list)

    # 用於存儲所有課程資料的 DataFrame
    all_courses_df = pd.DataFrame()
    courses_teacher_df = pd.DataFrame(columns=['課程代碼', '課程名稱', '學分', '教師'])

    # 為每門課程添加資料
    for course_code, course_name, credits, teacher in courses_data:
        random_state = random.randint(0, 100)
        num_students = random.randint(40, 50)  # 確保每門課程有 40~50 個學生
        selected_students = select_random_students(
            students_df, num_students, random_state=random_state)
        teacher_name, course_df = create_course_data(
            course_code, course_name, credits, teacher, selected_students)

        # 添加到總的資料框中
        all_courses_df = pd.concat(
            [all_courses_df, course_df], ignore_index=True)

        # 添加課程與教師對應的資料到 DataFrame
        courses_teacher_df = pd.concat([courses_teacher_df, pd.DataFrame([{
            '課程代碼': course_code,
            '課程名稱': course_name,
            '學分': credits,
            '教師': teacher
        }])], ignore_index=True)

    # 分離教師名稱和流水號
    courses_teacher_df[['教師名稱', '流水號']
                       ] = courses_teacher_df['教師'].str.extract(r'(\D+)(\d+)')
    courses_teacher_df['流水號'] = courses_teacher_df['流水號'].astype(int)

    # 根據教師名稱和流水號排序
    courses_teacher_df = courses_teacher_df.sort_values(
        by=['教師名稱', '流水號', '課程代碼'])

    # 刪除額外的列
    courses_teacher_df = courses_teacher_df.drop(columns=['教師名稱', '流水號'])

    # 確保目錄存在
    output_dir = 'build_course_data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 保存所有課程資料到一個 CSV 文件
    all_courses_df.to_csv(os.path.join(
        output_dir, 'all_courses_data.csv'), index=False, encoding='utf-8-sig')
    print("已創建 all_courses_data.csv")

    # # 保存課程與教師對應表到 CSV 文件
    # courses_teacher_df.to_csv(os.path.join(output_dir, 'courses_teacher.csv'), index=False, encoding='utf-8-sig')
    # print("已創建 courses_teacher.csv")


if __name__ == "__main__":
    main()
