# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.
import os
import pprint
import random
import re
import textwrap
from contextlib import redirect_stdout
from io import StringIO
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.ssaConverter import SSAConverter
from hintzCompiler.compiler import parseAndBuildCompilationContextFromInput
from flask import Flask, jsonify, render_template, request, send_file
from hintzCompiler.src.ssaDCE import SSAAwareDeadCodeElimination
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers
from hintzCompiler.src.hintz_dumper import HintzCfgDumper
from hintzCompiler.src.readWriteAnalyzer import ReadWriteAnalyzer

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

def _extract_code_snippets_from_text(test_text: str):
    snippets = []
    pattern = re.compile(r'code\s*=\s*(?P<q>"""|\'\'\')(?P<body>.*?)(?P=q)', re.DOTALL)
    for match in pattern.finditer(test_text):
        snippet = textwrap.dedent(match.group("body")).strip()
        if snippet:
            snippets.append(snippet)
    return snippets

def _load_random_samples_from_tests():
    tests_dir = os.path.join(os.path.dirname(__file__), "..", "tests")
    samples = []
    for root, _, files in os.walk(tests_dir):
        for filename in sorted(files):
            if not (filename.startswith("test_") and filename.endswith(".py")):
                continue
            path = os.path.join(root, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    samples.extend(_extract_code_snippets_from_text(f.read()))
            except OSError:
                continue

    # Remove duplicates while preserving order.
    deduped = list(dict.fromkeys(samples))
    return deduped

SAMPLE_PROGRAMS = _load_random_samples_from_tests()

def _rwa_as_text(cctx):
    if len(cctx.cfgs) == 0:
        return "No functions found. Read/Write analysis requires a function."
    rwa = ReadWriteAnalyzer(cctx.cfgs[0])
    buf = StringIO()
    with redirect_stdout(buf):
        rwa.dump()
    return buf.getvalue().strip()

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
            elif action == "rwa":
                ir_output = _rwa_as_text(cctx)

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
                    ir_output = HintzCfgDumper(cfg, de_ssa=True).dump()
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
                    cfg.makeCompact()
                    ir_output = HintzCfgDumper(cfg, de_ssa=True).dump()
                    dot_path = os.path.join(UPLOAD_DIR, "cfg.dot")
                    svg_path = os.path.join(UPLOAD_DIR, "cfg.svg")
                    cfg.to_graphviz(dot_path)
                    os.system(f"dot -Tsvg {dot_path} -o {svg_path}")
                    cfg_generated = True

        except Exception as e:
            ir_output = f"❌ Error: {str(e)}"

    return render_template("index.html", ir_output=ir_output, cfg_generated=cfg_generated)

@app.route("/random-sample", methods=["GET"])
def random_sample():
    if not SAMPLE_PROGRAMS:
        return jsonify({"code": "", "error": "No samples found"}), 404
    return jsonify({"code": random.choice(SAMPLE_PROGRAMS), "count": len(SAMPLE_PROGRAMS)})

@app.route("/static/cfg.svg")
def serve_svg():
    return send_file("static/cfg.svg")
