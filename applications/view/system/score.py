import os
from flask import Blueprint, request, render_template, jsonify, current_app

from applications.common.utils.http import fail_api, success_api, table_api
from applications.common.utils.rights import authorize
from applications.extensions import db
from applications.models import Score
from sqlalchemy import desc
from applications.schemas import ScoreOutSchema
from applications.common.curd import model_to_dicts
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
