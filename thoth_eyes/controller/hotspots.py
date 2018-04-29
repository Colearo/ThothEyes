#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from flask import Blueprint, flash, g, redirect, request, url_for, json
from ..orm import ORM

orm = ORM()
bp = Blueprint('hotspots', __name__, url_prefix='/api/hotspots')

@bp.route('/words/today', methods=["GET"])
def words_today() :
    today = datetime.datetime.today()
    today = today.strftime('%Y/%m/%d')
    d = orm.orm_topwords_by_date(today)
    return json.jsonify(d)

@bp.route('/words/date/<date>', methods=["GET"])
def words_date(date) :
    date = datetime.datetime.strptime(date, '%Y%m%d')
    date = date.strftime('%Y/%m/%d')
    d = orm.orm_topwords_by_date(date)
    return json.jsonify(d)

@bp.route('/subtopics/today', methods=["GET"])
def subtopics_today() :
    today = datetime.datetime.today()
    today = today.strftime('%Y/%m/%d')
    d = orm.orm_topsubtopics_by_date(today)
    return json.jsonify(d)

@bp.route('/subtopics/date/<date>', methods=["GET"])
def subtopics_date(date) :
    date = datetime.datetime.strptime(date, '%Y%m%d')
    date = date.strftime('%Y/%m/%d')
    d = orm.orm_topsubtopics_by_date(date)
    return json.jsonify(d)



