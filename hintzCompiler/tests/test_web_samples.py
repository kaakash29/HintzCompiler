# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from types import SimpleNamespace

import hintzCompiler.hintz_web.app as web_app


def test_extract_code_snippets_from_text():
    text = (
        "def test_a():\n"
        "    code = \"\"\"\n"
        "    int foo() {\n"
        "        return 1;\n"
        "    }\n"
        "    \"\"\"\n\n"
        "def test_b():\n"
        "    code = '''\n"
        "    int bar() {\n"
        "        return 2;\n"
        "    }\n"
        "    '''\n"
    )
    snippets = web_app._extract_code_snippets_from_text(text)
    assert len(snippets) == 2
    assert "int foo()" in snippets[0]
    assert "int bar()" in snippets[1]


def test_random_sample_endpoint_returns_sample(monkeypatch):
    monkeypatch.setattr(web_app, "SAMPLE_PROGRAMS", ["int main() { return 0; }"])
    client = web_app.app.test_client()
    response = client.get("/random-sample")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["code"] == "int main() { return 0; }"
    assert payload["count"] == 1


def test_rwa_action_renders_output(monkeypatch):
    fake_cctx = SimpleNamespace(_ast={}, cfgs=[], bbgs=[])
    monkeypatch.setattr(web_app, "get_cached_cctx", lambda code: fake_cctx)
    monkeypatch.setattr(web_app, "_rwa_as_text", lambda cctx: "[0] reads: [a], writes: [b]")

    client = web_app.app.test_client()
    response = client.post("/", data={"code": "int main(){ }", "action": "rwa"})
    assert response.status_code == 200
    assert b"[0] reads: [a], writes: [b]" in response.data
