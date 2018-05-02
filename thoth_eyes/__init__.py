#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template

def create_app(test_config = None) :
    app = Flask(__name__, instance_relative_config = True)

    if test_config is None :
        app.config.from_pyfile('config.py')
    else :
        app.config.from_mapping(test_config)
    
    try :
        os.makedirs(app.instance_path)
    except OSError :
        pass

    from .controller import subtopics
    app.register_blueprint(subtopics.bp)

    from .controller import hotspots
    app.register_blueprint(hotspots.bp)

    from .controller import timelines
    app.register_blueprint(timelines.bp)

    from .controller import topicsearch
    app.register_blueprint(topicsearch.bp)

    @app.route('/')
    def base() :
        return render_template('base.html')

    return app

