#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, flash, g, redirect, request, url_for, json
from ..orm import ORM

orm = ORM()
bp = Blueprint('topicsearch', __name__, url_prefix='/api/search')

@bp.route('/<searchwords>', methods=["GET"])
def searchwords(searchwords) :
    d = list()
    if searchwords.strip() is not '' :
        d = orm.orm_topicsearch_by_search(searchwords)
    return json.jsonify(d)

