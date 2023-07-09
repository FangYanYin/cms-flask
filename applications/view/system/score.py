import os,json
from flask import Blueprint, request, render_template, jsonify, current_app

from applications.common.utils.http import fail_api, success_api, table_api
from applications.common.utils.rights import authorize
from applications.extensions import db
from applications.models import Score
from sqlalchemy import desc
from applications.schemas import ScoreOutSchema
from applications.common.curd import model_to_dicts, auto_model_jsonify
from applications.common.utils.validate import str_escape

bp = Blueprint('adminScore', __name__, url_prefix='/score')


#  成绩管理
@bp.get('/')
@authorize("system:score:main")
def index():
    return render_template('system/score/score.html')


#  成绩数据
@bp.get('/table')
@authorize("system:score:main")
def table():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    school_year = str_escape(request.args.get('year', type=str))
    semester = str_escape(request.args.get('semester', type=str))
    course_name = str_escape(request.args.get('course', type=str))
    teacher_name = str_escape(request.args.get('teacher', type=str))
    filters = []
    if school_year:
        filters.append(Score.school_year.contains(school_year))
    if semester:
        filters.append(Score.semester.contains(semester))
    if course_name:
        filters.append(Score.course_name.contains(course_name))
    if teacher_name:
        filters.append(Score.teacher_name.contains(teacher_name))
    # orm查询
    # 使用分页获取data需要.items
    score = Score.query.filter(*filters).order_by(desc(Score.id)).paginate(page=page, per_page=limit, error_out=False)
    count = score.total
    return table_api(data= model_to_dicts(schema=ScoreOutSchema, data=score.items), count=count)

#  班级分析
@bp.get('/class')
@authorize("system:score:class")
def banji():
    return render_template('system/score/class.html')

#  班级数据
@bp.get('/class_data')
@authorize("system:score:class")
def banji_data():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    banji = str_escape(request.args.get('banji', type=str))
    filters = []
    if banji:
        filters.append(Score.banji.contains(banji))
    # 指定字段
    score = Score.query.distinct().with_entities(Score.banji, Score.major_name, Score.grade).filter(*filters).paginate(page=page, per_page=limit, error_out=False)
    count = score.total
    return table_api(data= model_to_dicts(schema=ScoreOutSchema, data=score.items), count=count)

#  班级图表数据
@bp.get('/class_chart')
@authorize("system:score:class")
def banji_chart():
    banji = str_escape(request.args.get('banji', type=str))
    filters = []
    if banji:
        filters.append(Score.banji.contains(banji))
    print(filters)
    categoryData = []
    seriesData = []
    courseNames = Score.query.distinct().with_entities(Score.course_name).filter(*filters).logic_all()
    count = Score.query.distinct().with_entities(Score.course_name).filter(*filters).count()
    a = b = c = d = e = 0;
    for courseName in courseNames:
        filters.append(Score.course_name.contains(courseName.course_name))
        # 保留4位小数 | 为了防止减了之后很多小数，外层round
        passRate = round(1 - (Score.query.filter(*filters).filter(Score.score < 59).count() / Score.query.filter(*filters).count()), 4)
        categoryData.append(courseName.course_name) 
        seriesData.append(round(passRate*100, 2)) 
        if passRate == 1:
            a += 1
        elif passRate > 0.9:
            b += 1
        elif passRate > 0.8:
            c += 1
        elif passRate > 0.2:
            d += 1
        else:
            e += 1
        filters.pop()
    # 排序
    categorySeries = zip(categoryData,seriesData)
    sortedCategorySeries = sorted(categorySeries,key=lambda x:x[1])
    result = zip(*sortedCategorySeries)
    sortedCategoryData, sortedSeriesData = [list(x) for x in result]

    res = {
        'msg': '',
        'count': count,
        'code': 0,
        'data':  {
            # 取前10个
            'category': sortedCategoryData[:10],
              'series': sortedSeriesData[:10],
              'pie' : [
                  { 'value': round(a / (a+b+c+d+e), 2), 'name': '优秀(100%)' },
                  { 'value': round(b / (a+b+c+d+e), 2), 'name': '掌握(90%~99%)' },
                  { 'value': round(c / (a+b+c+d+e), 2), 'name': '合格(80%~90%)' },
                  { 'value': round(d / (a+b+c+d+e), 2), 'name': '不合格(<80%)' },
                  { 'value': round(e / (a+b+c+d+e), 2), 'name': '⚠️(<20%)' }
                ]
              },
    }
    return jsonify(res)

#  单科分析
@bp.get('/single')
@authorize("system:score:single")
def single():
    return render_template('system/score/single.html')

#  单科数据
@bp.get('/single_data')
@authorize("system:score:single")
def single_data():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    school_year = str_escape(request.args.get('year', type=str))
    semester = str_escape(request.args.get('semester', type=str))
    course_name = str_escape(request.args.get('course', type=str))
    teacher_name = str_escape(request.args.get('teacher', type=str))
    filters = []
    if school_year:
        filters.append(Score.school_year.contains(school_year))
    if semester:
        filters.append(Score.semester.contains(semester))
    if course_name:
        filters.append(Score.course_name.contains(course_name))
    if teacher_name:
        filters.append(Score.teacher_name.contains(teacher_name))
    # orm查询
    # 使用分页获取data需要.items
    score = Score.query.filter(*filters).order_by(desc(Score.id)).paginate(page=page, per_page=limit, error_out=False)
    count = score.total
    return table_api(data= model_to_dicts(schema=ScoreOutSchema, data=score.items), count=count)

#   上传
@bp.get('/upload')
@authorize("system:score:add", log=True)
def upload():
    return render_template('system/photo/photo_add.html')


#   上传接口
@bp.post('/upload')
@authorize("system:score:add", log=True)
def upload_api():
    if 'file' in request.files:
        photo = request.files['file']
        mime = request.files['file'].content_type

        file_url = upload_curd.upload_one(photo=photo, mime=mime)
        res = {
            "msg": "上传成功",
            "code": 0,
            "success": True,
            "data":
                {"src": file_url}
        }
        return jsonify(res)
    return fail_api()


#    成绩删除
@bp.route('/delete', methods=['GET', 'POST'])
@authorize("system:score:delete", log=True)
def delete():
    _id = request.form.get('id')
    res = upload_curd.delete_photo_by_id(_id)
    if res:
        return success_api(msg="删除成功")
    else:
        return fail_api(msg="删除失败")


#   成绩批量删除
@bp.route('/batchRemove', methods=['GET', 'POST'])
@authorize("system:score:delete", log=True)
def batch_remove():
    ids = request.form.getlist('ids[]')
    photo_name = Score.query.filter(Score.id.in_(ids)).all()
    upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
    for p in photo_name:
        os.remove(upload_url + '/' + p.name)
    photo = Score.query.filter(Score.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    if photo:
        return success_api(msg="删除成功")
    else:
        return fail_api(msg="删除失败")
