from flask import Flask, render_template, request, send_file
from hintzCompiler.compiler import compile_source
from hintzCompiler.src.cfg import ControlFlowGraph
import os
import pprint

app = Flask(__name__)
UPLOAD_DIR = "static"

@app.route("/", methods=["GET", "POST"])
def index():
    ir_output = ""
    cfg_generated = False

    if request.method == "POST":
        code = request.form["code"]
        action = request.form["action"]

        try:
            ir = compile_source(code)
            if action == "ast":
                ir_output = pprint.pformat(ir, indent=2)
            elif action == "cfg":
                function = ir.declarations[0]
                cfg = ControlFlowGraph(function)
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")
                cfg.to_graphviz(dot_path)
                os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                cfg_generated = True
        except Exception as e:
            ir_output = f"❌ Error: {str(e)}"

    return render_template("index.html", ir_output=ir_output, cfg_generated=cfg_generated)

@app.route("/static/cfg.svg")
def serve_svg():
    return send_file("static/cfg.svg")
