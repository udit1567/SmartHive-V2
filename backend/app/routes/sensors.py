from flask import Blueprint, jsonify, request

from app.auth import get_device_user
from app.extensions import db
from app.models import Data

bp = Blueprint("sensors", __name__)


def get_latest_non_null(user_id, column):
    latest_entry = (
        Data.query.filter(getattr(Data, column).isnot(None), Data.user_id == user_id)
        .order_by(Data.timestamp.desc())
        .first()
    )

    if latest_entry:
        return jsonify(
            {
                column: getattr(latest_entry, column),
                "timestamp": latest_entry.timestamp.strftime("%d %B %Y %H:%M"),
            }
        )
    return jsonify({"message": f"No valid data found for {column}"}), 404


@bp.route("/get_data/<int:id>", methods=["GET"])
def get_data(id):
    data = Data.query.filter_by(user_id=id).all()
    if not data:
        return {"message": "No data found for this user."}, 404

    data_dict = [
        {
            "id": item.id,
            "D1": item.D1,
            "D2": item.D2,
            "D3": item.D3,
            "D4": item.D4,
            "D5": item.D5,
            "D6": item.D6,
            "D7": item.D7,
            "D8": item.D8,
            "timestamp": item.timestamp.isoformat() if item.timestamp else None,
            "user_id": item.user_id,
        }
        for item in data
    ]
    return {"data": data_dict}, 200


@bp.route("/update", methods=["POST"])
def update_data():
    user, error = get_device_user()
    if error:
        return error

    payload = request.get_json() or {}
    new_data = Data(
        D1=payload.get("D1"),
        D2=payload.get("D2"),
        D3=payload.get("D3"),
        D4=payload.get("D4"),
        D5=payload.get("D5"),
        D6=payload.get("D6"),
        D7=payload.get("D7"),
        D8=payload.get("D8"),
        user_id=user.id,
    )
    db.session.add(new_data)
    db.session.commit()
    return {"message": "Data successfully updated.", "data": new_data.to_dict()}, 200


@bp.route("/get_d1/<int:id>", methods=["GET"])
def get_d1(id):
    return get_latest_non_null(id, "D1")


@bp.route("/get_d2/<int:id>", methods=["GET"])
def get_d2(id):
    return get_latest_non_null(id, "D2")


@bp.route("/get_d3/<int:id>", methods=["GET"])
def get_d3(id):
    return get_latest_non_null(id, "D3")


@bp.route("/get_d4/<int:id>", methods=["GET"])
def get_d4(id):
    return get_latest_non_null(id, "D4")


@bp.route("/get_d5/<int:id>", methods=["GET"])
def get_d5(id):
    return get_latest_non_null(id, "D5")


@bp.route("/get_d6/<int:id>", methods=["GET"])
def get_d6(id):
    return get_latest_non_null(id, "D6")


@bp.route("/get_d7/<int:id>", methods=["GET"])
def get_d7(id):
    return get_latest_non_null(id, "D7")


@bp.route("/get_d8/<int:id>", methods=["GET"])
def get_d8(id):
    return get_latest_non_null(id, "D8")
