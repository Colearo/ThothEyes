#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from flask import Blueprint, flash, g, redirect, request, url_for, json
from ..orm import ORM

orm = ORM()
bp = Blueprint('subtopics', __name__, url_prefix='/api/subtopics')

@bp.route('/today', methods=["GET"])
def today() :
    today = datetime.datetime.today()
    today = today.strftime('%Y/%m/%d')
    page = request.args.get('page')
    size = request.args.get('size')

    if page is None or size is None :
        d = orm.orm_subtopics_by_date(today)
    else :
        d = orm.orm_subtopics_by_pageandsize(today, int(page), int(size))
    return json.jsonify(d)


@bp.route('/today/total', methods=["GET"])
def today_total() :
    today = datetime.datetime.today()
    today = today.strftime('%Y/%m/%d')
    d = orm.orm_subtopicstotal_by_date(today)
    return json.jsonify(d)


@bp.route('/date/<date>', methods=["GET"])
def date_subs(date) :
    page = request.args.get('page')
    size = request.args.get('size')
    date = datetime.datetime.strptime(date, '%Y%m%d')
    date = date.strftime('%Y/%m/%d')

    if page is None or size is None :
        d = orm.orm_subtopics_by_date(date)
    else :
        d = orm.orm_subtopics_by_pageandsize(date, int(page), int(size))
    return json.jsonify(d)

@bp.route('/date/<date>/total', methods=["GET"])
def date_subs_total(date) :
    date = datetime.datetime.strptime(date, '%Y%m%d')
    date = date.strftime('%Y/%m/%d')
    d = orm.orm_subtopicstotal_by_date(date)
    return json.jsonify(d)


