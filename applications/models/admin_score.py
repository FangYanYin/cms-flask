import datetime
from applications.extensions import db


class Score(db.Model):
    __tablename__ = 'admin_score'
    id = db.Column(db.Integer, primary_key=True)
    school_year = db.Column(db.String(32), nullable=False, comment='学年')
    semester = db.Column(db.String(2), nullable=False, comment='学期')
    student_no = db.Column(db.String(64), nullable=False, comment='学号')
    student_name = db.Column(db.String(128), nullable=False, comment='姓名')
    sex = db.Column(db.String(4), nullable=False, comment='性别')
    course_no = db.Column(db.String(32), comment='课程代码')
    course_name = db.Column(db.String(128), comment='课程名称')
    opening_college = db.Column(db.String(128), comment='开课学院')
    course_nature = db.Column(db.String(32), comment='课程性质')
    credit = db.Column(db.String(16), comment='学分')
    score = db.Column(db.String(8), comment='成绩')
    course_type = db.Column(db.String(16), comment='课程类别')
    teacher_name = db.Column(db.String(64), comment='任课老师')
    grade = db.Column(db.String(16), comment='年级')
    major_name = db.Column(db.String(64), comment='专业名称')
    banji = db.Column(db.String(32), comment='班级')
    study_time = db.Column(db.String(8), comment='学时')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment='更新时间')
    delete_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='删除时间')