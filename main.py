try:
    import tkinter as tk
    from tkinter import messagebox
    import tkinter.font as tkFont
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image, ImageTk
    from io import BytesIO
    from matplotlib import rcParams

    # 設定 Matplotlib 字體
    rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    rcParams['axes.unicode_minus'] = False
    
except ImportError as e:
    print(f"發生 ImportError: {e}")
    exit(1)

class DataManager:
    def __init__(self):
        self.all_courses_data = self.load_all_courses_data()

        self.student_data = self.load_student_data()
        self.teacher_data = self.load_teacher_data()

    def add_column(self, df):
        # 計算總成績
        df['總成績'] = round((df['期中考'] * 0.3 + df['期末考']* 0.3 + df['平時成績'] * 0.4), 2)

        # 計算 GPA
        df['GPA'] = df['總成績'].apply(self.grade_to_GPA)

        # 計算排名
        df['期中考排名'] = df.groupby('課程代碼')['期中考'].rank(ascending=False, method='min').astype(int)
        df['期末考排名'] = df.groupby('課程代碼')['期末考'].rank(ascending=False, method='min').astype(int)
        df['平時成績排名'] = df.groupby('課程代碼')['平時成績'].rank(ascending=False, method='min').astype(int)
        df['總排名'] = df.groupby('課程代碼')['總成績'].rank(ascending=False, method='min').astype(int)

        df['總人數'] = df.groupby('課程代碼')['學號'].transform('count')

        df['期中考排名'] = df['期中考排名'].astype(int)
        df['期末考排名'] = df['期末考排名'].astype(int)
        df['平時成績排名'] = df['平時成績排名'].astype(int)
        df['總成績排名'] = df['總排名'].astype(int)

        # 計算 GPA 排名
        df['GPA排名'] = df.groupby('課程名稱')['GPA'].rank(
            ascending=False, method='min').astype(int)
        df['GPA排名'] = df['GPA排名'].astype(int)

        return df

    def load_all_courses_data(self):
        try:
            df = pd.read_csv(r'save_data\all_courses_data.csv', encoding='utf-8-sig', dtype={'學號': str})
            df = self.add_column(df)
            return df
        except Exception as e:
            messagebox.showerror("錯誤", f"載入 all_courses_data.csv 檔案失敗：{e}")
            exit(1)

    def load_student_data(self):
        try:
            return pd.read_csv(r'save_data\student_data.csv', encoding='utf-8-sig', dtype={'學號': str, '密碼': str})
        except Exception as e:
            messagebox.showerror("錯誤", f"載入 student_data.csv 檔案失敗：{e}")
            exit(1)

    def load_teacher_data(self):
        try:
            return pd.read_csv(r'save_data\teacher_data.csv', encoding='utf-8-sig', dtype={'帳號': str, '密碼': str})
        except Exception as e:
            messagebox.showerror("錯誤", f"載入 teacher_data.csv 檔案失敗：{e}")
            exit(1)
    def save_all_courses_data(self, df):
        df=df.drop(columns=['總成績','GPA','期中考排名','期末考排名','平時成績排名','總排名','總人數','總成績排名','GPA排名'])

        df.to_csv(r'save_data\all_courses_data.csv',encoding='utf-8-sig', index=False)
        print("save")

    @staticmethod
    def grade_to_GPA(grade):
        gpa_mapping = {
            (90, 100): 4.3,
            (85, 90): 4.0,
            (80, 85): 3.7,
            (77, 80): 3.3,
            (73, 77): 3.0,
            (70, 73): 2.7,
            (67, 70): 2.4,
            (63, 67): 2.0,
            (60, 63): 1.7,
            (50, 60): 1.0,
            (0, 50): 0,
        }
        for key, value in gpa_mapping.items():
            if grade >= key[0] and grade < key[1]:
                return value

class GradeSystemApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("成績查詢與管理系統")
        self.state('zoomed')  # 最大化視窗

        # 存取資料
        self.datas = DataManager()
        # 讀取學生和教師帳密資料
        self.students_df = self.datas.load_student_data()
        self.teachers_df = self.datas.load_teacher_data()
        # 建立並顯示登錄 Frame
        self.login_frame = LoginFrame(self, self.students_df, self.teachers_df)
        # 初始化其他 Frame
        self.students_frame = None
        self.teacher_frame = None

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_frame(self, frame):
        frame.tkraise()

    def on_closing(self):
        if messagebox.askokcancel("確認退出", "您確定要退出嗎？"):
            plt.close('all')  # 關閉所有 Matplotlib 圖形
            self.destroy()

    def show_student_frame(self, student_name):
        if self.students_frame is not None:
            self.students_frame.destroy()
        self.students_frame = StudentFrame(self, student_name)
        self.students_frame.place(
            relx=0.5, rely=0.5, anchor='center', relwidth=1, relheight=1)

    def show_teacher_frame(self, teacher_name):
        if self.teacher_frame is not None:
            self.teacher_frame.destroy()
        self.teacher_frame = TeacherFrame(self, teacher_name)
        self.teacher_frame.place(
            relx=0.5, rely=0.5, anchor='center', relwidth=1, relheight=1)

    def show_login_frame(self):
        # 隱藏學生和教師的畫面，如果已經建立
        if self.students_frame is not None:
            self.students_frame.destroy()
            self.students_frame = None  # 清空變數
        if self.teacher_frame is not None:
            self.teacher_frame.destroy()
            self.teacher_frame = None  # 清空變數

        # 建立並顯示登錄 Frame
        self.login_frame = LoginFrame(self, self.students_df, self.teachers_df)

        self.show_frame(self.login_frame)


class LoginFrame(tk.Frame):
    def __init__(self, parent, students_df, teachers_df):
        super().__init__(parent)
        self.configure(bg='lightgray')
        self.students_df = students_df  # 存儲學生帳號和密碼資料
        self.teachers_df = teachers_df  # 存儲教師帳號和密碼資料
        # 設置字體
        font_style_label = tkFont.Font(family="Arial", size=25)
        font_style_button = tkFont.Font(family="Arial", size=25, weight="bold")
        font_style_topics = tkFont.Font(size=30, weight="bold")

        # 設置窗口大小和位置
        self.place(relx=0.5, rely=0.5, anchor='center',relwidth=0.8, relheight=0.6)

        # 標題
        tk.Label(self, text="成績查詢與管理系統", bg='lightgray', font=font_style_topics).place(
            relx=0.5, rely=0.1, anchor='center')
        # 身份選擇
        tk.Label(self, text="身份", bg='lightgray', font=font_style_label).place(
            relx=0.3, rely=0.3, anchor='e')
        self.role_var = tk.StringVar(value="student")
        tk.Radiobutton(self, text="學生", variable=self.role_var, value="student",
                    bg='lightgray', font=font_style_label).place(relx=0.35, rely=0.3, anchor='w')
        tk.Radiobutton(self, text="教師", variable=self.role_var, value="teacher",
                    bg='lightgray', font=font_style_label).place(relx=0.55, rely=0.3, anchor='w')

        # 帳號和密碼標籤及輸入框
        tk.Label(self, text="帳號", bg='lightgray', font=font_style_label).place(
            relx=0.3, rely=0.4, anchor='e')
        self.username_entry = tk.Entry(self, font=font_style_label)
        self.username_entry.place(
            relx=0.35, rely=0.4, anchor='w', relwidth=0.4)

        tk.Label(self, text="密碼", bg='lightgray', font=font_style_label).place(relx=0.3, rely=0.5, anchor='e')
        self.password_entry = tk.Entry(self, show="*", font=font_style_label)
        self.password_entry.place(relx=0.35, rely=0.5, anchor='w', relwidth=0.4)

        # 登錄按鈕
        tk.Button(self, text="登錄", command=self.login, font=font_style_button).place(
            relx=0.4, rely=0.7, anchor='center')

        # 清除按鈕
        tk.Button(self, text="清除", command=self.clear_entries,
                font=font_style_button).place(relx=0.6, rely=0.7, anchor='center')

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if username and password:
            if role == "student":
                student_row = self.students_df[self.students_df['學號'] == username]
                if not student_row.empty and student_row['密碼'].values[0] == password:
                    student_name = student_row['姓名'].values[0]
                    self.master.show_student_frame(student_name)
                else:
                    messagebox.showerror("錯誤", "帳號或密碼錯誤")
            elif role == 'teacher':
                teacher_row = self.teachers_df[self.teachers_df['帳號'] == username]
                if not teacher_row.empty and teacher_row['密碼'].values[0] == password:
                    teacher_name = teacher_row['姓名'].values[0]
                    self.master.show_teacher_frame(teacher_name)
                else:
                    messagebox.showerror("錯誤", "帳號或密碼錯誤")
        else:
            messagebox.showerror("錯誤", "請輸入帳號和密碼")

class StudentFrame(tk.Frame):
    def __init__(self, parent, student_name):
        super().__init__(parent)

        self.student_name = student_name
        self.all_course_datas_df = self.master.datas.all_courses_data  # 使用 DataManager 實例
        self.course_list = self.load_courses()
        self.course_list.append("all 所有課程")
        # 設置字體
        font_style_label = tkFont.Font(family="Arial", size=25)
        font_style_button = tkFont.Font(family="Arial", size=20, weight="bold")
        font_style_optionmenu = tkFont.Font(family="Arial", size=20)

        # 設置列和行的權重，以使其自適應
        for i in range(20):
            self.grid_columnconfigure(i, weight=1)
            # self.grid_rowconfigure(i, weight=1)

        # 設置介面
        self.lbl = tk.Label(
            self, text=f"{student_name}，請選擇課程", font=font_style_label)
        self.lbl.grid(row=0, column=6, columnspan=6, sticky=tk.NE+tk.SW)
        self.course_var = tk.StringVar(value="請選擇")
        self.selected_course_id = None
        self.selected_course_name = None
        self.course_dropdown = tk.OptionMenu(
            self, self.course_var, *self.course_list, command=self.course_selected)
        self.course_dropdown.config(font=font_style_optionmenu)
        self.course_dropdown.grid(
            row=0, column=12, columnspan=3, sticky=tk.NE+tk.SW)
        # 設置 OptionMenu 的選項字體
        menu = self.course_dropdown['menu']
        menu.config(font=font_style_optionmenu)

        self.logout_button = tk.Button(
            self, text="登出", font=font_style_button, command=self.logout)
        self.logout_button.grid(
            row=0, column=18, columnspan=2, sticky=tk.NE+tk.SW)

        tk.Label(self, text=f"選擇操作：", font=("Arial", 20)).grid(
            row=4, column=6, columnspan=2, sticky=tk.NW+tk.SE)
        # 添加按鈕
        tk.Button(self, text="查看成績", font=("Arial", 20), command=self.view_grade_table).grid(
            row=4, column=8, columnspan=3, sticky=tk.NW+tk.SE)
        tk.Button(self, text="查看圖表", font=("Arial", 20), command=self.view_grade_chart).grid(
            row=4, column=12, columnspan=3, sticky=tk.NW+tk.SE)
        # 創建畫布
        self.canvas = tk.Canvas(self, width=800, height=600, bg='white')
        self.canvas.grid(row=5, column=0,
                         columnspan=20, sticky=tk.NE+tk.SW)

        # 儲存圖像對象
        self.image_tk = None

    def load_courses(self):
        """從 DataManager 讀取學生選修的課程列表，並顯示為'課程代碼 課程名稱'"""
        df = self.all_course_datas_df
        student_courses = df[df['姓名'] == self.student_name][[
            '課程代碼', '課程名稱']].drop_duplicates()
        return [f"{row['課程代碼']} {row['課程名稱']}" for _, row in student_courses.iterrows()]

    def course_selected(self, selected_course):
        """處理課程選擇事件"""
        self.selected_course_id = selected_course.split(' ')[0]  # #課程代碼
        self.selected_course_name = selected_course.split(' ')[1]  # 只取課程
        self.clear_canvas()

    def clear_canvas(self):
        """清除畫布上的內容"""
        self.canvas.delete("all")
        self.image_tk = None

    def draw_picture(self, fig):
        """將 Matplotlib 圖像繪製到 Tkinter 畫布"""
        # 將圖表保存為圖像
        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        img_tk = ImageTk.PhotoImage(img)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        # img = img.resize((400, 300), Image.Resampling.LANCZOS)
        # 清除畫布內容
        self.clear_canvas()

        # 獲取畫布中心座標
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = img.size
        print(img_width, img_height)
        print(canvas_width, canvas_height)
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2

        # 顯示圖像
        self.canvas.create_image(x,y, image=img_tk,anchor=tk.NW)
        self.canvas.image = img_tk  # 保持對圖像的引用，防止被垃圾回收

    def view_grade_table(self):
        if self.selected_course_name == "所有課程":
            self.create_all_courses_table()
        else:
            self.create_grade_table()

    def view_grade_chart(self):
        if self.selected_course_name == "所有課程":
            self.create_all_courses_chart()
        else:
            self.create_grade_chart()

    def create_grade_table(self):
        if self.selected_course_name == None:
            messagebox.showwarning("警告", "請選擇課程")
            return 0
        """顯示成績表格"""
        # 讀取成績數據
        df = self.all_course_datas_df
        course_data = df[(df['姓名'] == self.student_name) & (df['課程代碼'] == self.selected_course_id)]

        # 準備表格數據
        columns = ["期中考", "期末考", "平時成績", "總成績", "GPA"]
        values = [course_data[col].values[0] if col in course_data.columns else "未提供" for col in columns]
        rankings = [course_data[col + "排名"].values[0]
                    if (col + "排名") in course_data.columns else "未提供" for col in columns]
        # 使用 Matplotlib 顯示表格
        fig, ax = plt.subplots(figsize=(20, 20))
        ax.axis('tight')
        ax.axis('off')
        # 設置表格數據
        table_data = [[columns[i], values[i], rankings[i]] for i in range(len(columns))]

        # 創建表格
        table = ax.table(cellText=table_data, colLabels=[
                         "項目", "成績", "排名"], cellLoc='center', loc='center', colColours=['lightgrey'] * 3)
        
        # 設定表格字型
        font_properties = {'family': 'Microsoft JhengHei',
                           'weight': 'bold', 'size': 14}
        font_title_properties = {
            'family': 'Microsoft JhengHei', 'weight': 'bold', 'size': 20}

        for key, cell in table.get_celld().items():
            text = cell._text
            text.set_fontproperties(font_properties)
            if key[0] == 0 or key[1] == 0:  # Header row or column
                text.set_fontsize(16)
                text.set_fontweight('bold')
            else:
                text.set_fontsize(14)

        # 調整單元格的寬度和高度
        for key, cell in table.get_celld().items():
            if key[0] == 0:
                cell.set_edgecolor('black')
                cell.set_linewidth(1)
            cell.set_width(0.1)  # 調整單元格寬度
            cell.set_height(0.05)  # 調整單元格高度

            cell.set_edgecolor('black')  # 設定邊框顏色
            cell.set_linewidth(1)  # 設定邊框寬度
            cell.set_facecolor(
                # 設定單元格背景顏色
                'lightgrey' if key[0] == 0 or key[1] == 0 else 'white')

        ax.set_title(f'{self.selected_course_name} 成績分析',
                     fontdict=font_title_properties)
        # 將圖像顯示在畫布上
        
        self.draw_picture(fig)

    def create_grade_chart(self):
        if self.selected_course_name == None:
            messagebox.showwarning("警告", "請選擇課程")
            return 0
        """顯示成績圖表"""
        # 讀取課程數據
        df = self.all_course_datas_df
        course_data = df[(df['姓名'] == self.student_name) &
                         (df['課程代碼'] == self.selected_course_id)]

        if course_data.empty:
            messagebox.showwarning("警告", "該課程沒有數據")
            return

        # 字型
        font_title_properties = {
            'family': 'Microsoft JhengHei', 'weight': 'bold', 'size': 20}
        # 繪製長條圖
        fig, ax = plt.subplots(figsize=(6, 4))
        subjects = ["期中考", "期末考", "平時成績", "總成績"]
        scores = [course_data[subject].values[0] for subject in subjects]

        ax.bar(subjects, scores, color=['blue', 'green', 'orange', '#ba55d3'])
        ax.set_xlabel('項目')
        ax.set_ylabel('成績')
        ax.set_ylim(0, 100)
        ax.set_title(f'{self.selected_course_name} 成績分析',
                     fontdict=font_title_properties,pad=0.001)

        # 將圖像顯示在畫布上
        self.draw_picture(fig)

    def create_all_courses_table(self):
        """顯示所有課程的表格"""
        # 讀取學生所有課程的數據
        df = self.all_course_datas_df
        student_courses_data = df[df['姓名'] == self.student_name]

        if student_courses_data.empty:
            messagebox.showwarning("警告", "該學生沒有課程數據")
            return
        columns = ["課程名稱", "學分", "期中考", "期末考", "平時成績", "總成績", "GPA"]
        table_data = student_courses_data[columns].values.tolist()
        # 計算平均GPA
        average_gpa = 0
        if 'GPA' in student_courses_data.columns and '學分' in student_courses_data.columns:
            total_credits = student_courses_data['學分'].sum()
            weighted_gpa_sum = (
                student_courses_data['GPA'] * student_courses_data['學分']).sum()
            average_gpa = weighted_gpa_sum / total_credits if total_credits != 0 else 0

        # 使用 Matplotlib 顯示表格
        fig, ax = plt.subplots(figsize=(17, len(table_data) +2))  # 調整高度以適應數據行數
        ax.axis('tight')
        ax.axis('off')

        # 設置表格數據
        table = ax.table(cellText=table_data, colLabels=columns,
                        cellLoc='center', loc='center', colColours=['lightgrey'] * len(columns))

        # 設定字型
        font_properties = {'family': 'Microsoft JhengHei', 'weight': 'bold', 'size': 20}
        font_title_properties = {'family': 'Microsoft JhengHei', 'weight': 'bold', 'size': 24}

        # 設定每個欄位的寬度
        column_widths = {'課程名稱': 0.2, '學分': 0.05, '期中考': 0.1, '期末考': 0.1, '平時成績': 0.1, '總成績': 0.1, 'GPA': 0.05}

        # 調整單元格的寬度和高度
        for key, cell in table.get_celld().items():
            if key[0] == 0:  # Header row
                cell.set_edgecolor('black')
                cell.set_linewidth(1)
            if len(key)<5:
                h=0.1
            elif len(key)<7:
                h=0.05
            else:
                h=0.03
            cell.set_height(h)  # 調整單元格高度
            # 根據欄位名稱設置寬度
            col_name = columns[key[1]]
            cell.set_width(column_widths.get(col_name, 0.15))  # 默認寬度
            
            cell.set_edgecolor('black')  # 設定邊框顏色
            cell.set_linewidth(1)  # 設定邊框寬度
            cell.set_facecolor('lightgrey' if key[0] == 0 else 'white')  # 設定單元格背景顏色
        
        # 設置字型屬性
        for key, cell in table.get_celld().items():
            text = cell._text
            text.set_fontproperties(font_properties)
            if key[0] == 0:  # Header row
                text.set_fontsize(20)
                text.set_fontweight('bold')
            else:
                text.set_fontsize(16)
        
        # ax.set_title('所有課程成績表', fontdict=font_title_properties,pad=0.001)
        
        # 在表格下方顯示平均GPA
        text_str = f"平均GPA: {average_gpa:.2f}"
        plt.figtext(0.5, 0.05, text_str, ha='center', va='center',
                    fontsize=14, fontfamily='Microsoft JhengHei', weight='bold')
        
        # 將圖像顯示在畫布上
        self.draw_picture(fig)

    def create_all_courses_chart(self):
        """顯示所有課程的圖表"""
        # 讀取學生所有課程的數據
        df = self.all_course_datas_df
        student_courses_data = df[df['姓名'] == self.student_name]

        if student_courses_data.empty:
            messagebox.showwarning("警告", "該學生沒有課程數據")
            return

        # 字型
        font_title_properties = {
            'family': 'Microsoft JhengHei', 'weight': 'bold', 'size': 20}
        # 繪製長條圖
        fig, ax = plt.subplots(figsize=(10, 6))
        courses = student_courses_data['課程名稱'].tolist()
        midterm_scores = student_courses_data['期中考'].tolist()
        final_scores = student_courses_data['期末考'].tolist()
        casual_scores = student_courses_data['平時成績'].tolist()
        total_scores = student_courses_data['總成績'].tolist()

        x = range(len(courses))
        ax.bar(x, midterm_scores, width=0.2,
               label='期中考', color='blue', align='center')
        ax.bar([p + 0.2 for p in x], final_scores, width=0.2,
               label='期末考', color='green', align='center')
        ax.bar([p + 0.4 for p in x], casual_scores, width=0.2,
               label='平時成績', color='orange', align='center')
        ax.bar([p + 0.6 for p in x], total_scores, width=0.2,
               label='總成績', color='#ba55d3', align='center')

        ax.set_xticks([p + 0.3 for p in x])
        ax.set_xticklabels(courses, rotation=45, ha='right')
        ax.set_xlabel('課程名稱')
        ax.set_ylabel('成績')
        ax.set_ylim(0, 100)
        ax.set_title('所有課程成績分析', fontdict=font_title_properties)
        ax.legend()

        # 將圖像顯示在畫布上
        self.draw_picture(fig)

    def logout(self):
        """登出並返回登錄界面"""
        if messagebox.askyesno("確認", "是否要登出"):
            self.destroy()
            app.show_login_frame()

class TeacherFrame(tk.Frame):
    def __init__(self, parent, teacher_name):
        super().__init__(parent)

        self.teacher_name = teacher_name
        self.all_course_datas_df = self.master.datas.all_courses_data  # 使用 DataManager 實例
        self.course_list = self.load_courses(self.teacher_name)

        # 設置字體
        font_style_label = tkFont.Font(family="Arial", size=25)
        font_style_button = tkFont.Font(family="Arial", size=20, weight="bold")
        font_style_optionmenu = tkFont.Font(family="Arial", size=20)

        # 設置列和行的權重，以使其自適應
        for i in range(20):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

        # 設置介面
        self.lbl = tk.Label(
            self, text=f"{self.teacher_name}，請選擇課程", font=font_style_label)
        self.lbl.grid(row=0, column=4, rowspan=1,
                      columnspan=5, sticky=tk.NE+tk.SW)
        self.course_var = tk.StringVar(value="請選擇")
        self.selected_course_id = None
        self.selected_course_name = None
        self.selected_course = None
        self.course_dropdown = tk.OptionMenu(
            self, self.course_var, *self.course_list, command=self.course_selected)
        self.course_dropdown.config(font=font_style_optionmenu)
        self.course_dropdown.grid(
            row=0, column=9, rowspan=1, columnspan=3, sticky=tk.NE+tk.SW)
        # 設置 OptionMenu 的選項字體
        menu = self.course_dropdown['menu']
        menu.config(font=font_style_optionmenu)

        tk.Label(self, text="選擇操作：", font=("Arial", 20)).grid(
            row=1, column=4, columnspan=4, sticky=tk.NE+tk.SW)
        tk.Button(self, text="查看學生成績", font=("Arial", 20),
                  command=self.view_students_table).grid(row=1, column=8, columnspan=2, rowspan=1, sticky=tk.NE+tk.SW)
        tk.Button(self, text="修改學生成績", font=("Arial", 20),
                  command=self.modify_grade).grid(row=1, column=10, columnspan=2, rowspan=1, sticky=tk.NE+tk.SW)
        tk.Button(self, text="查看圖表", font=("Arial", 20),
                  command=self.view_grade_chart).grid(row=1, column=12, columnspan=2, rowspan=1, sticky=tk.NE+tk.SW)

        # 登出按鈕
        self.logout_button = tk.Button(
            self, text="登出", font=font_style_button, command=self.logout)
        self.logout_button.grid(row=0, column=18, columnspan=2)
        self.act_frame = None
        self.table_frame = None
        self.canvas = None
        self.set_frame()

        # 儲存圖像對象
        self.image_tk = None

    def set_frame(self, t='frame'):
        if self.act_frame is not None:
            self.act_frame.destroy()
        if self.table_frame is not None:
            self.table_frame.destroy()
        if self.canvas is not None:
            self.canvas.destroy()
        if t == 'frame':
            # 根據選擇而出現不同的內容
            self.act_frame = tk.Frame(self)
            self.act_frame.grid(row=2, column=0, rowspan=1,
                                columnspan=20, sticky=tk.NE+tk.SW)
            for i in range(20):
                self.act_frame.grid_columnconfigure(i, weight=1)
            # 創建畫布
            self.table_frame = tk.Frame(self)
            self.table_frame.grid(
                row=4, column=0, rowspan=13, columnspan=20, sticky=tk.NE+tk.SW)
            for i in range(20):
                self.table_frame.grid_columnconfigure(i, weight=1)
            for i in range(13):
                self.table_frame.grid_rowconfigure(i, weight=1)
        else:
            self.act_frame = tk.Frame(self)
            self.act_frame.grid(row=2, column=0, rowspan=1,
                                columnspan=20, sticky=tk.NE+tk.SW)
            for i in range(20):
                self.act_frame.grid_columnconfigure(i, weight=1)
            self.canvas = tk.Canvas(self, width=800, height=600)
            self.canvas.grid(row=4, column=0, rowspan=15,
                             columnspan=20, sticky=tk.NE+tk.SW)

    def load_courses(self, teachername):
        """從 CSV 文件中加載教師修課的課程列表"""
        df = self.all_course_datas_df

        # 去除教師名稱中的前後空格，避免因空格導致的匹配錯誤
        df['教師'] = df['教師'].str.strip()

        # 確保教師名稱為字串並去除前後空格
        teacher_name = str(teachername).strip()

        # 過濾出符合教師名稱的課程資料
        student_courses = df[df['教師'].str.strip() == teacher_name][[
            '課程代碼', '課程名稱']].drop_duplicates()

        # 返回課程代碼和名稱的列表
        return [f"{row['課程代碼']} {row['課程名稱']}" for _, row in student_courses.iterrows()]

    def course_selected(self, selected_course):
        """處理課程選擇事件"""
        self.selected_course = selected_course
        self.selected_course_id, self.selected_course_name = selected_course.split(
            ' ')
        self.clear()

    def clear(self):
        """清除畫布上的內容"""
        self.set_frame()
        self.image_tk = None

    def view_students_table(self):
        if self.selected_course is None:
            messagebox.showwarning("警告", "請先選擇課程")
            return
        Radiobuttonfont = tkFont.Font(family="Arial", size=16)
        self.set_frame("image")
        self.role_var = tk.StringVar(value="default")
        # 創建排序選項的單選按鈕，並在command中傳遞action參數
        tk.Radiobutton(self.act_frame, text="預設", variable=self.role_var, value="default",
                       command=lambda: self.create_students_table("default"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=5, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="依學號排序", variable=self.role_var, value="id",
                       command=lambda: self.create_students_table("id"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=7, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="依期中考成績排序", variable=self.role_var, value="mid",
                       command=lambda: self.create_students_table("mid"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=9, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="依期末考成績排序", font=Radiobuttonfont, variable=self.role_var, value="final",
                       command=lambda: self.create_students_table("final"), indicatoron=False).grid(row=0, column=11, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="依平時成績排序", variable=self.role_var, value="casual",
                       command=lambda: self.create_students_table("casual"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=13, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="依總成績排序", variable=self.role_var, value="avg",
                       command=lambda: self.create_students_table("avg"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=15, columnspan=2, sticky=tk.NE+tk.SW)

        # 初始表格顯示
        self.create_students_table("default")

    def create_students_table(self, action):
        # 從 all_course_datas_df 中篩選出選定課程的數據
        df = self.all_course_datas_df[self.all_course_datas_df['課程代碼']
                                      == self.selected_course_id]

        if df.empty:
            messagebox.showwarning("警告", "該課程沒有數據")
            return

        # 根據選定的排序方式進行排序
        if action == "id":
            df = df.sort_values(by="學號")
            columns = ['學號', '姓名', '期中考', '期末考', '平時成績', '總成績', 'GPA']
        elif action == "mid":
            df = df.sort_values(by="期中考", ascending=False)
            columns = ['期中考排名', '學號', '姓名', '期中考', '期末考', '平時成績', '總成績', 'GPA']

        elif action == "final":
            df = df.sort_values(by="期末考", ascending=False)
            columns = ['期末考排名', '學號', '姓名', '期中考', '期末考', '平時成績', '總成績', 'GPA']

        elif action == "casual":
            df = df.sort_values(by="平時成績", ascending=False)
            columns = ['平時成績排名', '學號', '姓名',
                       '期中考', '期末考', '平時成績', '總成績', 'GPA']
        elif action == "avg":
            df = df.sort_values(by="總成績", ascending=False)
            columns = ['總成績排名', '學號', '姓名', '期中考', '期末考', '平時成績', '總成績', 'GPA']
        elif action == "default":
            df = df  # 不進行排序，使用原始順序
            columns = ['學號', '姓名', '期中考', '期末考', '平時成績', '總成績', 'GPA']
        # 將數據分為兩部分
        df_part1 = df.head(25)
        df_part2 = df.tail(len(df) - 25) if len(df) > 25 else pd.DataFrame()

        # 創建兩張 Matplotlib 圖像
        fig, axs = plt.subplots(1, 2, figsize=(20, 8))

        # 繪製第一張圖
        df_part1 = df_part1[columns]
        df_part1['學號'] = df_part1['學號'].astype(str)

        table_data = df_part1.values
        col_labels = df_part1.columns

        # 設置表格樣式
        axs[0].axis('tight')
        axs[0].axis('off')

        table = axs[0].table(cellText=table_data, colLabels=col_labels,
                             cellLoc='center', loc='center', colWidths=[0.1] * len(col_labels))
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(1.2, 1.2)

        # 設置標題列顏色
        for (i, j), cell in table._cells.items():
            if i == 0:
                cell.set_facecolor('lightgray')

        # 繪製第二張圖
        if not df_part2.empty:
            df_part2 = df_part2[columns]
            df_part2['學號'] = df_part2['學號'].astype(str)

            table_data = df_part2.values
            col_labels = df_part2.columns

            # 設置表格樣式
            axs[1].axis('tight')
            axs[1].axis('off')

            table = axs[1].table(cellText=table_data, colLabels=col_labels,
                                 cellLoc='center', loc='center', colWidths=[0.1] * len(col_labels))
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            table.scale(1.2, 1.2)

            # 設置標題列顏色
            for (i, j), cell in table._cells.items():
                if i == 0:
                    cell.set_facecolor('lightgray')
        else:
            axs[1].axis('off')  # 如果沒有剩餘的數據，隱藏第二張圖

        plt.tight_layout()
        self.draw_picture(fig)

    def view_grade_chart(self):
        if self.selected_course is None:
            messagebox.showwarning("警告", "請先選擇課程")
            return

        Labelfont = tkFont.Font(family="Arial", size=16)
        Radiobuttonfont = tkFont.Font(family="Arial", size=16)
        self.set_frame("image")
        self.role_var = tk.StringVar(value="default")
        # 創建排序選項的單選按鈕，並在command中傳遞action參數
        tk.Label(self.act_frame, text="選擇圖表資料類型", font=Labelfont).grid(
            row=0, column=4, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="期中考", variable=self.role_var, value="mid",
                       command=lambda: self.create_grade_chart("mid"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=7, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="期末考", variable=self.role_var, value="final",
                       command=lambda: self.create_grade_chart("final"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=9, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="平時成績", variable=self.role_var, value="casual",
                       command=lambda: self.create_grade_chart("casual"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=11, columnspan=2, sticky=tk.NE+tk.SW)
        tk.Radiobutton(self.act_frame, text="總成績", variable=self.role_var, value="avg",
                       command=lambda: self.create_grade_chart("avg"), font=Radiobuttonfont, indicatoron=False).grid(row=0, column=13, columnspan=2, sticky=tk.NE+tk.SW)

    def create_grade_chart(self, action):
        if self.selected_course is None:
            messagebox.showwarning("警告", "請先選擇課程")
            return

        df = self.all_course_datas_df[self.all_course_datas_df['課程代碼']
                                      == self.selected_course_id]

        if df.empty:
            messagebox.showwarning("警告", "該課程沒有數據")
            return

        # 根據 action 選擇對應的成績列
        if action == "mid":
            scores = df["期中考"]
            title = "期中考成績分布"
        elif action == "final":
            scores = df["期末考"]
            title = "期末考成績分布"
        elif action == "casual":
            scores = df["平時成績"]
            title = "平時成績分布"
        elif action == "avg":
            scores = df["總成績"]
            title = "總成績分布"
        else:
            messagebox.showerror("錯誤", "無效的選擇")
            return

        # 設置圖表
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(scores, bins=10, range=(0, 100), edgecolor='black', alpha=0.7)
        ax.set_title(title, fontsize=18)
        ax.set_xlabel("分數", fontsize=14)
        ax.set_ylabel("人數", fontsize=14)
        ax.set_xticks(range(0, 101, 10))  # 設置 x 軸的刻度

        # 顯示平均數和中位數
        mean_score = scores.mean()
        median_score = scores.median()
        ax.axvline(mean_score, color='red', linestyle='dashed', linewidth=1)
        ax.axvline(median_score, color='green',
                   linestyle='dashed', linewidth=1)
        ax.text(mean_score + 1, max(ax.get_ylim()) * 0.9,
                f'平均數: {mean_score:.1f}', color='red')
        ax.text(median_score + 1, max(ax.get_ylim()) * 0.8,
                f'中位數: {median_score:.1f}', color='green')

        plt.tight_layout()

        self.draw_picture(fig)

    def draw_picture(self, fig):
        """將 Matplotlib 圖像繪製到 Tkinter 畫布"""
        # 將圖表保存為圖像
        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        img_tk = ImageTk.PhotoImage(img)
        # 獲取畫布大小
        canvas_width = 1550
        canvas_height = 600
        # 縮放圖片以符合畫布大小
        img_width, img_height = img.size
        scale_width = canvas_width / img_width
        scale_height = canvas_height / img_height
        scale = min(scale_width, scale_height)

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        # 計算中心位置
        x_center = (canvas_width - new_width) // 2
        y_center = (canvas_height - new_height) // 2
        # 顯示圖像
        self.canvas.create_image(
            x_center, y_center, anchor=tk.NW, image=img_tk)
        self.canvas.image = img_tk  # 保持對圖像的引用，防止被垃圾回收
    def modify_grade(self):
        if self.selected_course == None:
            messagebox.showwarning("警告", "請先選擇課程")
            return 0
        self.set_frame()
        font_style_label = tkFont.Font(family="Arial", size=25)
        font_style_button = tkFont.Font(family="Arial", size=25)

        tk.Label(self.act_frame, text="請輸入學生姓名或學號:", font=font_style_label).grid(
            row=0, column=5, columnspan=4)
        student_name_entry = tk.Entry(self.act_frame, font=font_style_label)
        student_name_entry.grid(row=0, column=9, columnspan=2)

        def on_confirm():
            student_name_or_id = student_name_entry.get()
            student_data = self.get_student_data(student_name_or_id)

            if student_data is None:
                messagebox.showerror("錯誤", "找不到該學生")
                return

            self.display_student_grades(student_data)
        tk.Button(self.act_frame, text="確認", font=font_style_button,
                  command=on_confirm).grid(row=0, column=11, columnspan=2)

    def get_student_data(self, student_name_or_id):
        df = self.all_course_datas_df
        student_data = df[(df['課程代碼'] == self.selected_course_id) & (
            (df['學號'] == student_name_or_id) | (df['姓名'] == student_name_or_id))]

        if not student_data.empty:
            return student_data.iloc[0]  # 返回第一筆找到的資料
        else:
            return None

    def display_student_grades(self, student_data):
        font_style_label = tkFont.Font(family="Arial", size=25)

        tk.Label(self.table_frame, text=f"{student_data['姓名']}", font=font_style_label).grid(
            row=0, column=8, columnspan=4)
        tk.Label(self.table_frame, text="項目", font=font_style_label).grid(
            row=2, column=6, columnspan=4)
        tk.Label(self.table_frame, text="期中考", font=font_style_label).grid(
            row=4, column=6, columnspan=4)
        tk.Label(self.table_frame, text="期末考", font=font_style_label).grid(
            row=6, column=6, columnspan=4)
        tk.Label(self.table_frame, text="平時成績", font=font_style_label).grid(
            row=8, column=6, columnspan=4)

        tk.Label(self.table_frame, text="修改成績", font=font_style_label).grid(
            row=2, column=9, columnspan=4)
        midterm_entry = tk.Entry(self.table_frame, font=font_style_label)
        midterm_entry.insert(0, str(student_data['期中考']))
        midterm_entry.grid(row=4, column=11, columnspan=2)

        final_entry = tk.Entry(self.table_frame, font=font_style_label)
        final_entry.insert(0, str(student_data['期末考']))
        final_entry.grid(row=6, column=11, columnspan=2)

        casual_entry = tk.Entry(self.table_frame, font=font_style_label)
        casual_entry.insert(0, str(student_data['平時成績']))
        casual_entry.grid(row=8, column=11, columnspan=2)

        def on_save():
            # 更新資料
            self.all_course_datas_df.loc[self.all_course_datas_df['學號']
                                         == student_data['學號'], '期中考'] = float(midterm_entry.get())
            self.all_course_datas_df.loc[self.all_course_datas_df['學號']
                                         == student_data['學號'], '期末考'] = float(final_entry.get())
            self.all_course_datas_df.loc[self.all_course_datas_df['學號']
                                         == student_data['學號'], '平時成績'] = float(casual_entry.get())

            self.all_course_datas_df = self.master.datas.add_column(self.all_course_datas_df)
            self.save_data()  # 儲存數據
            messagebox.showinfo("成功", "成績已更新")

        tk.Button(self.table_frame, text="儲存", font=font_style_label,
                  command=on_save).grid(row=10, column=9, columnspan=4)

    def save_data(self):
        # 儲存更新後的數據
        self.master.datas.save_all_courses_data(self.all_course_datas_df)

    def logout(self):
        if messagebox.askyesno("確認", "是否要登出"):
            self.destroy()
            app.show_login_frame()


if __name__ == "__main__":
    app = GradeSystemApp()
    app.mainloop()
