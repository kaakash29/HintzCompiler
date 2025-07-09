# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.
import os
import pprint

from typing import cast
from hintzCompiler.compiler import Driver
from hintzCompiler.src.ir_nodes import Function
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.basic_blocks import BasicBlockGraph
from flask import Flask, render_template, request, send_file
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers

app = Flask(__name__)
UPLOAD_DIR = "static"

@app.route("/", methods=["GET", "POST"])
def index():
    ir_output = ""
    cfg_generated = False
    cfg_generated = False

    if request.method == "POST":
        code = request.form["code"]
        action = request.form["action"]

        try:
            ast = Driver(code).ast
            if action == "ast":
                ir_output = pprint.pformat(ast, indent=2)

            elif action == "cfg":
                function = cast(Function, ast.declarations[0])
                cfg = ControlFlowGraph(function)
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")
                cfg.to_graphviz(dot_path)
                os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                cfg_generated = True

            elif action == "bbg":
                function = cast(Function, ast.declarations[0])
                cfg = ControlFlowGraph(function)
                bbg = BasicBlockGraph(cfg)
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")
                bbg.to_graphviz(dot_path)
                os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                cfg_generated = True

            elif action == "dmt":
                function = cast(Function, ast.declarations[0])
                cfg = ControlFlowGraph(function)
                bbg = BasicBlockGraph(cfg)
                dom = Dominators(bbg)
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")
                dom.to_graphviz(dot_path)
                os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                cfg_generated = True

            elif action == "toSSA":
                function = cast(Function, ast.declarations[0])
                cfg = ControlFlowGraph(function)
                bbg = BasicBlockGraph(cfg)
                dom = Dominators(bbg)
                domFronts = DominanceFrontiers(dom)
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")
                domFronts.doms.bbg.cfg.to_graphviz(dot_path)
                os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                cfg_generated = True

        except Exception as e:
            ir_output = f"❌ Error: {str(e)}"

    return render_template("index.html", ir_output=ir_output, cfg_generated=cfg_generated)

@app.route("/static/cfg.svg")
def serve_svg():
    return send_file("static/cfg.svg")
