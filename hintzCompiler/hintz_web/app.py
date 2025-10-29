# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.
import os
import pprint
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.ssaConverter import SSAConverter
from hintzCompiler.compiler import parseAndBuildCompilationContextFromInput
from flask import Flask, render_template, request, send_file
from hintzCompiler.src.ssaDCE import SSAAwareDeadCodeElimination
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers

# Global cache (keyed by source code string)
from hashlib import sha256
cctx_cache = {}

def get_cached_cctx(code: str):
    key = sha256(code.encode()).hexdigest()
    if key not in cctx_cache:
        cctx_cache[key] = parseAndBuildCompilationContextFromInput(code)
    return cctx_cache[key]

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

        cctx = get_cached_cctx(code)

        try:
            ast = cctx._ast
            if action == "ast":
                ir_output = pprint.pformat(ast, indent=2)

            elif action == "cfg":
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")
               
                if len(cctx.cfgs) == 0:
                    with open(svg_path, 'w') as f:
                        pass  # File is created and remains empty
                else:
                    cfg = cctx.cfgs[0]
                    cfg.to_graphviz(dot_path)
                    os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                    cfg_generated = True

            elif action == "bbg":
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")

                if len(cctx.bbgs) == 0:
                    with open(svg_path, 'w') as f:
                        pass  # File is created and remains empty
                else:
                    bbg = cctx.bbgs[0]
                    bbg.to_graphviz(dot_path)
                    os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                    cfg_generated = True

            elif action == "dmt":
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")

                if len(cctx.bbgs) == 0:
                    with open(svg_path, 'w') as f:
                        pass  # File is created and remains empty
                else: 
                    bbg = cctx.bbgs[0]
                    dom = Dominators(bbg)
                    dom.to_graphviz(dot_path)
                    os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                    cfg_generated = True

            elif action == "toSSA":
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")

                if len(cctx.bbgs) == 0:
                    with open(svg_path, 'w') as f:
                        pass  # File is created and remains empty
                else: 
                    bbg = cctx.bbgs[0]
                    dom = Dominators(bbg)
                    domFronts = DominanceFrontiers(dom)

                    toSSA = SSAConverter(domFronts)
                    toSSA.doit()
                    
                    cfg = cctx.cfgs[0]
                    dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                    svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")
                    cfg.to_graphviz(dot_path)
                    os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                    cfg_generated = True

            elif action == "ssaDCE":
                dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")

                if len(cctx.bbgs) == 0:
                    with open(svg_path, 'w') as f:
                        pass  # File is created and remains empty
                else: 
                    bbg = cctx.bbgs[0]
                    dom = Dominators(bbg)
                    domFronts = DominanceFrontiers(dom)

                    ssaDCE = SSAAwareDeadCodeElimination(cctx.cfgs[0])
                    ssaDCE.doit()
                    
                    cfg = cctx.cfgs[0]
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
