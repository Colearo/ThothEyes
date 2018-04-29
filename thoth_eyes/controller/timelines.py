#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from flask import Blueprint, flash, g, redirect, request, url_for, json
from ..orm import ORM

orm = ORM()
bp = Blueprint('timelines', __name__, url_prefix='/api/timelines')

@bp.route('/days/<int:days>', methods=["GET"])
def days(days) :
    d = orm.orm_timelines_by_days(days)
    return json.jsonify(d)

