from applications.extensions import ma
from marshmallow import fields


class ScoreOutSchema(ma.Schema):
    id = fields.Integer()
    school_year = fields.Str()
    semester = fields.Str()
    student_no = fields.Str()
    student_name = fields.Str()
    sex = fields.Str()
    course_no = fields.Str()
    course_name = fields.Str()
    opening_college = fields.Str()
    course_nature = fields.Str()
    credit = fields.Str()
    score = fields.Str()
    course_type = fields.Str()
    teacher_name = fields.Str()
    grade = fields.Str()
    major_name = fields.Str()
    banji = fields.Str()
    course_type = fields.Str()
    study_time = fields.Str()
