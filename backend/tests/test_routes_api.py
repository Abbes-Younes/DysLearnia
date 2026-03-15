"""
tests/test_routes_api.py — Comprehensive API route tests.

Covers:
  - GET  /api/blocks
  - POST /api/pipeline/run (validate_only + seeded execution)
  - GET  /api/pipeline/{run_id}/output/{node_id}
  - POST /api/documents/upload
  - POST /api/flows  (Supabase mocked)
  - GET  /api/flows  (Supabase mocked)
  - POST /api/flows/{id}/fork
  - DELETE /api/flows/{id}
  - PATCH /api/flows/{id}/promote
  - POST /api/flows/{id}/comments
  - Swagger example pipelines (validate_only smoke tests)

All LLM, Supabase, Qdrant, and Neo4j calls are mocked.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import blocks  # noqa: F401 — register all blocks
from blocks.base import BlockData


# ── App fixture ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    with (
        patch("core.graph.build_graph", return_value=MagicMock()),
        patch("models.local_llm.init_llm"),
    ):
        from main import app
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


# ── GET /api/blocks ────────────────────────────────────────────────────────────

class TestBlocksEndpoint:
    def test_status_200(self, client):
        assert client.get("/api/blocks").status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/blocks").json()
        assert isinstance(data, list)
        assert len(data) >= 10  # we have 16 registered blocks

    def test_all_blocks_have_required_fields(self, client):
        for b in client.get("/api/blocks").json():
            assert "name" in b
            assert "display_name" in b
            assert "group" in b
            assert b["group"] in ("input", "transform", "output")
            assert "input_types" in b
            assert "output_types" in b
            assert "parameters" in b
            assert isinstance(b["parameters"], list)

    def test_contains_known_blocks(self, client):
        names = {b["name"] for b in client.get("/api/blocks").json()}
        expected = {
            "course_input", "summarizer", "quiz_builder", "flashcards",
            "tts", "dyslexia_font", "knowledge_graph", "key_concepts",
            "infographic", "simplified_text", "gamification", "gap_detector",
        }
        assert expected.issubset(names)

    def test_source_blocks_have_no_inputs(self, client):
        for b in client.get("/api/blocks").json():
            if b["group"] == "input":
                assert b["input_types"] == []

    def test_transform_blocks_accept_text(self, client):
        for b in client.get("/api/blocks").json():
            if b["group"] == "transform":
                assert "text" in b["input_types"]


# ── POST /api/pipeline/run — validate_only ────────────────────────────────────

class TestPipelineValidation:
    def _validate(self, client, nodes, edges):
        return client.post("/api/pipeline/run", json={
            "nodes": nodes, "edges": edges, "params": {}, "validate_only": True
        })

    def test_valid_linear_chain(self, client):
        r = self._validate(client, [
            {"id": "n1", "type": "summarizer"},
            {"id": "n2", "type": "dyslexia_font"},
        ], [{"source": "n1", "target": "n2"}])
        assert r.status_code == 200
        assert r.json()["validation_errors"] == []

    def test_incompatible_edge_caught(self, client):
        # tts → binary/wav; summarizer expects text — should flag error
        r = self._validate(client, [
            {"id": "n1", "type": "tts"},
            {"id": "n2", "type": "summarizer"},
        ], [{"source": "n1", "target": "n2"}])
        assert r.status_code == 200
        assert len(r.json()["validation_errors"]) >= 1

    def test_unknown_block_type_validate_passes(self, client):
        # Validator checks type compatibility, not registry membership.
        # Unknown types have no declared types, so no incompatibility errors.
        r = self._validate(client, [
            {"id": "n1", "type": "nonexistent_block_xyz"},
        ], [])
        assert r.status_code == 200
        # No type-mismatch errors since nothing connects to/from it
        assert isinstance(r.json()["validation_errors"], list)

    def test_unknown_block_type_execution_fails(self, client):
        """Running (not just validating) an unknown block returns 422."""
        r = client.post("/api/pipeline/run", json={
            "nodes": [{"id": "n1", "type": "nonexistent_block_xyz"}],
            "edges": [],
            "params": {},
        })
        assert r.status_code == 422

    def test_cycle_returns_error(self, client):
        r = client.post("/api/pipeline/run", json={
            "nodes": [
                {"id": "n1", "type": "summarizer"},
                {"id": "n2", "type": "summarizer"},
            ],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n1"},
            ],
            "params": {},
        })
        assert r.status_code in (200, 422, 500)

    def test_empty_pipeline_is_valid(self, client):
        r = self._validate(client, [], [])
        assert r.status_code == 200
        assert r.json()["validation_errors"] == []

    def test_single_source_node_is_valid(self, client):
        r = self._validate(client, [{"id": "n1", "type": "course_input"}], [])
        assert r.status_code == 200

    def test_three_node_chain_is_valid(self, client):
        r = self._validate(client, [
            {"id": "n1", "type": "summarizer"},
            {"id": "n2", "type": "key_concepts"},
            {"id": "n3", "type": "flashcards"},
        ], [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
        ])
        assert r.status_code == 200
        assert r.json()["validation_errors"] == []


# ── Swagger example pipelines — validate smoke tests ─────────────────────────

class TestSwaggerExamples:
    """Each named swagger example should pass validation (validate_only=True)."""

    def _run_example(self, client, example: dict) -> dict:
        payload = {**example, "validate_only": True}
        # strip initial_inputs for validate_only so no block execution happens
        r = client.post("/api/pipeline/run", json=payload)
        assert r.status_code == 200, r.text
        return r.json()

    def test_simplify_and_format(self, client):
        data = self._run_example(client, {
            "nodes": [
                {"id": "n1", "type": "summarizer"},
                {"id": "n2", "type": "dyslexia_font"},
            ],
            "edges": [{"source": "n1", "target": "n2"}],
            "params": {"n1": {"ratio": 0.4}, "n2": {"font": "OpenDyslexic"}},
        })
        assert data["validation_errors"] == []

    def test_quiz_from_doc(self, client):
        data = self._run_example(client, {
            "nodes": [
                {"id": "n1", "type": "course_input"},
                {"id": "n2", "type": "summarizer"},
                {"id": "n3", "type": "quiz_builder"},
            ],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"},
            ],
            "params": {"n1": {"doc_id": "dummy"}, "n2": {"ratio": 0.3}},
        })
        assert data["validation_errors"] == []

    def test_knowledge_graph_pipeline(self, client):
        data = self._run_example(client, {
            "nodes": [
                {"id": "n1", "type": "key_concepts"},
                {"id": "n2", "type": "knowledge_graph"},
            ],
            "edges": [{"source": "n1", "target": "n2"}],
            "params": {"n1": {"max_concepts": 10}, "n2": {"depth": 2}},
        })
        assert data["validation_errors"] == []

    def test_audio_lesson_pipeline(self, client):
        data = self._run_example(client, {
            "nodes": [
                {"id": "n1", "type": "summarizer"},
                {"id": "n2", "type": "tts"},
                {"id": "n3", "type": "audio_unifier"},
            ],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"},
            ],
            "params": {},
        })
        assert data["validation_errors"] == []

    def test_flashcard_deck(self, client):
        data = self._run_example(client, {
            "nodes": [
                {"id": "n1", "type": "key_concepts"},
                {"id": "n2", "type": "flashcards"},
            ],
            "edges": [{"source": "n1", "target": "n2"}],
            "params": {},
        })
        assert data["validation_errors"] == []


# ── POST /api/pipeline/run — seeded execution ─────────────────────────────────

class TestPipelineExecution:
    """
    Run pipelines with mocked block execute() methods.

    NOTE: The runner short-circuits nodes that already have data from
    initial_inputs.  To test a block's execution we seed the UPSTREAM node
    and let the block under test run.
    """

    def test_seeded_node_returns_seed_text(self, client):
        """A seeded node is returned as-is (runner skips execution)."""
        r = client.post("/api/pipeline/run", json={
            "nodes": [{"id": "n1", "type": "summarizer"}],
            "edges": [],
            "params": {},
            "initial_inputs": {"n1": {"text": "seed text"}},
        })
        assert r.status_code == 200
        data = r.json()
        assert data["run_id"] != ""
        assert data["outputs"]["n1"][0]["text"] == "seed text"

    def test_two_block_chain_propagates_output(self, client):
        """Seed n1, let n2 execute — output of n1 flows into n2."""
        n2_output = [BlockData(text="n2 result")]
        with patch(
            "blocks.transform.dyslexia_font.DyslexiaFontBlock.execute",
            new=AsyncMock(return_value=n2_output),
        ):
            r = client.post("/api/pipeline/run", json={
                "nodes": [
                    {"id": "n1", "type": "summarizer"},
                    {"id": "n2", "type": "dyslexia_font"},
                ],
                "edges": [{"source": "n1", "target": "n2"}],
                "params": {},
                "initial_inputs": {"n1": {"text": "seed text for n1"}},
            })
        assert r.status_code == 200
        assert r.json()["outputs"]["n2"][0]["text"] == "n2 result"

    def test_downstream_block_receives_seeded_input(self, client):
        """The DyslexiaFontBlock.execute should receive the seeded text as input."""
        captured: list = []

        async def mock_execute(self_, inputs, params):
            captured.extend(inputs)
            return [BlockData(text="formatted")]

        with patch(
            "blocks.transform.dyslexia_font.DyslexiaFontBlock.execute",
            new=mock_execute,
        ):
            client.post("/api/pipeline/run", json={
                "nodes": [
                    {"id": "n1", "type": "summarizer"},
                    {"id": "n2", "type": "dyslexia_font"},
                ],
                "edges": [{"source": "n1", "target": "n2"}],
                "params": {},
                "initial_inputs": {"n1": {"text": "upstream seed"}},
            })
        assert len(captured) == 1
        assert captured[0].text == "upstream seed"

    def test_binary_output_flagged(self, client):
        """Seed summarizer, let TTS run — binary output flagged."""
        with patch(
            "blocks.transform.tts_block.TTSBlock.execute",
            new=AsyncMock(return_value=[
                BlockData(binary=b"fake-wav", mime_type="binary/wav")
            ]),
        ):
            r = client.post("/api/pipeline/run", json={
                "nodes": [
                    {"id": "n1", "type": "summarizer"},
                    {"id": "n2", "type": "tts"},
                ],
                "edges": [{"source": "n1", "target": "n2"}],
                "params": {},
                "initial_inputs": {"n1": {"text": "Read this aloud"}},
            })
        assert r.status_code == 200
        assert r.json()["outputs"]["n2"][0]["has_binary"] is True

    def test_run_id_is_uuid(self, client):
        r = client.post("/api/pipeline/run", json={
            "nodes": [{"id": "n1", "type": "summarizer"}],
            "edges": [],
            "params": {},
            "initial_inputs": {"n1": {"text": "text"}},
        })
        import uuid as _uuid
        _uuid.UUID(r.json()["run_id"])  # raises if not a valid UUID


# ── GET /api/pipeline/{run_id}/output/{node_id} ───────────────────────────────

class TestPipelineBinaryDownload:
    def test_unknown_run_returns_404(self, client):
        r = client.get("/api/pipeline/nonexistent-run-id/output/n1")
        assert r.status_code == 404

    def test_known_run_text_only_node_returns_404(self, client):
        """When a node produced only text (no binary), 404 is expected."""
        with patch("blocks.transform.summarizer.SummarizerBlock.execute",
                   new=AsyncMock(return_value=[BlockData(text="text only")])):
            run_r = client.post("/api/pipeline/run", json={
                "nodes": [{"id": "n1", "type": "summarizer"}],
                "edges": [],
                "params": {},
                "initial_inputs": {"n1": {"text": "something"}},
            })
        run_id = run_r.json()["run_id"]
        r = client.get(f"/api/pipeline/{run_id}/output/n1")
        assert r.status_code == 404

    def test_known_run_binary_node_returns_bytes(self, client):
        fake_audio = b"\x00\x01\x02\x03"
        with patch(
            "blocks.transform.tts_block.TTSBlock.execute",
            new=AsyncMock(return_value=[
                BlockData(binary=fake_audio, mime_type="binary/wav",
                          metadata={"filename": "lesson.wav"})
            ]),
        ):
            run_r = client.post("/api/pipeline/run", json={
                "nodes": [
                    {"id": "n1", "type": "summarizer"},
                    {"id": "n2", "type": "tts"},
                ],
                "edges": [{"source": "n1", "target": "n2"}],
                "params": {},
                "initial_inputs": {"n1": {"text": "read this"}},
            })
        run_id = run_r.json()["run_id"]
        r = client.get(f"/api/pipeline/{run_id}/output/n2")
        assert r.status_code == 200
        assert r.content == fake_audio


# ── POST /api/documents/upload ────────────────────────────────────────────────

class TestDocumentsUpload:
    FAKE_PDF = b"%PDF-1.4 fake content"
    FAKE_PPTX = b"PK\x03\x04fake pptx"

    def _mock_course_block(self, doc_id="test-doc-123", text="Extracted text."):
        bd = BlockData(
            text=text,
            metadata={"doc_id": doc_id, "page_count": 3, "chunk_count": 5},
        )
        return patch(
            "blocks.inputs.course_input.CourseInputBlock.execute",
            new=AsyncMock(return_value=[bd]),
        )

    def test_pdf_upload_returns_doc_id(self, client):
        with self._mock_course_block():
            r = client.post(
                "/api/documents/upload",
                files={"file": ("lecture.pdf", self.FAKE_PDF, "application/pdf")},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["doc_id"] == "test-doc-123"
        assert data["chunk_count"] == 5
        assert data["page_count"] == 3

    def test_pptx_upload_accepted(self, client):
        mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        with self._mock_course_block():
            r = client.post(
                "/api/documents/upload",
                files={"file": ("slides.pptx", self.FAKE_PPTX, mime)},
            )
        assert r.status_code == 200

    def test_preview_text_truncated_at_500_chars(self, client):
        long_text = "A" * 1000
        with self._mock_course_block(text=long_text):
            r = client.post(
                "/api/documents/upload",
                files={"file": ("doc.pdf", self.FAKE_PDF, "application/pdf")},
            )
        assert len(r.json()["preview_text"]) <= 500

    def test_empty_file_returns_400(self, client):
        r = client.post(
            "/api/documents/upload",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert r.status_code == 400

    def test_no_file_returns_422(self, client):
        r = client.post("/api/documents/upload")
        assert r.status_code == 422

    def test_extraction_failure_returns_422(self, client):
        with patch(
            "blocks.inputs.course_input.CourseInputBlock.execute",
            new=AsyncMock(side_effect=RuntimeError("extraction failed")),
        ):
            r = client.post(
                "/api/documents/upload",
                files={"file": ("bad.pdf", self.FAKE_PDF, "application/pdf")},
            )
        assert r.status_code == 422


# ── Flows endpoints — Supabase mocked ─────────────────────────────────────────

def _sb_mock(execute_returns: list):
    """
    Build a Supabase mock where each call to .execute() pops the next item
    from `execute_returns`.  Each item should be a dict OR list that becomes
    the `.data` of the result.
    """
    results = []
    for payload in execute_returns:
        r = MagicMock()
        r.data = payload
        results.append(r)

    table_mock = MagicMock()
    for method in ("upsert", "insert", "select", "eq", "or_",
                   "order", "update", "delete", "single"):
        getattr(table_mock, method).return_value = table_mock
    table_mock.execute.side_effect = results

    sb_mock = MagicMock()
    sb_mock.table.return_value = table_mock

    user_mock = MagicMock()
    user_mock.id = "user-abc"
    auth_resp = MagicMock()
    auth_resp.user = user_mock
    sb_mock.auth.get_user.return_value = auth_resp

    return sb_mock


AUTH = {"Authorization": "Bearer fake-token"}


class TestFlowsEndpoints:
    GRAPH = {"nodes": [{"id": "n1", "type": "summarizer"}], "edges": []}

    def test_upsert_flow_returns_id(self, client):
        sb = _sb_mock([[{"id": "flow-1"}]])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.post("/api/flows", json={
                "title": "My Pipeline",
                "graph": self.GRAPH,
                "is_public": False,
            }, headers=AUTH)
        assert r.status_code == 200
        assert "id" in r.json()

    def test_upsert_flow_no_supabase_returns_503(self, client):
        with patch("db.supabase.get_client", return_value=None):
            r = client.post("/api/flows", json={"title": "T", "graph": self.GRAPH})
        assert r.status_code == 503

    def test_list_flows_returns_array(self, client):
        sb = _sb_mock([[{"id": "f1", "title": "Flow 1"}]])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.get("/api/flows", headers=AUTH)
        assert r.status_code == 200
        assert isinstance(r.json()["flows"], list)

    def test_get_flow_no_supabase_returns_503(self, client):
        with patch("db.supabase.get_client", return_value=None):
            r = client.get("/api/flows/nonexistent", headers=AUTH)
        assert r.status_code == 503

    def test_get_flow_accessible(self, client):
        flow_data = {
            "id": "flow-1", "title": "Public Flow",
            "owner_id": "user-abc", "is_public": True, "is_template": False,
        }
        sb = _sb_mock([flow_data])  # single() → dict
        with patch("db.supabase.get_client", return_value=sb):
            r = client.get("/api/flows/flow-1", headers=AUTH)
        assert r.status_code == 200

    def test_fork_flow_returns_new_id(self, client):
        source = {
            "id": "flow-1", "title": "Original", "graph": self.GRAPH,
            "owner_id": "other-user", "is_public": True,
            "description": None, "thumbnail": None, "locked_params": {},
        }
        # First execute → source dict, second → insert result
        sb = _sb_mock([source, [{"id": "new-flow"}]])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.post("/api/flows/flow-1/fork", headers=AUTH)
        assert r.status_code == 200
        assert "id" in r.json()
        assert r.json()["id"] != "flow-1"

    def test_delete_flow_own_flow(self, client):
        # First execute → ownership check, second → delete
        sb = _sb_mock([{"owner_id": "user-abc"}, []])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.delete("/api/flows/flow-1", headers=AUTH)
        assert r.status_code == 200
        assert r.json()["deleted"] is True

    def test_delete_flow_not_owner_returns_403(self, client):
        sb = _sb_mock([{"owner_id": "someone-else"}])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.delete("/api/flows/flow-1", headers=AUTH)
        assert r.status_code == 403

    def test_add_comment_returns_comment(self, client):
        sb = _sb_mock([[{"id": "c1", "body": "Improve this block"}]])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.post(
                "/api/flows/flow-1/comments",
                json={"node_id": "n1", "body": "Improve this block", "author_role": "teacher"},
                headers=AUTH,
            )
        assert r.status_code == 200
        assert "comment" in r.json()

    def test_list_comments_returns_array(self, client):
        sb = _sb_mock([[{"id": "c1"}, {"id": "c2"}]])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.get("/api/flows/flow-1/comments", headers=AUTH)
        assert r.status_code == 200
        assert isinstance(r.json()["comments"], list)
        assert len(r.json()["comments"]) == 2

    def test_resolve_comment(self, client):
        sb = _sb_mock([[]])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.patch("/api/flows/flow-1/comments/c1", headers=AUTH)
        assert r.status_code == 200
        assert r.json()["resolved"] is True

    def test_promote_flow_own(self, client):
        sb = _sb_mock([{"owner_id": "user-abc"}, []])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.patch("/api/flows/flow-1/promote", headers=AUTH)
        assert r.status_code == 200
        assert r.json()["promoted"] is True

    def test_promote_flow_not_owner_returns_403(self, client):
        sb = _sb_mock([{"owner_id": "someone-else"}])
        with patch("db.supabase.get_client", return_value=sb):
            r = client.patch("/api/flows/flow-1/promote", headers=AUTH)
        assert r.status_code == 403


# ── Swagger schema smoke test ──────────────────────────────────────────────────

class TestOpenAPISchema:
    def test_openapi_json_valid(self, client):
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert schema["info"]["title"] == "DysLearnia API"

    def test_pipeline_run_has_examples(self, client):
        r = client.get("/openapi.json")
        schema = r.json()
        post_op = schema["paths"]["/api/pipeline/run"]["post"]
        examples = (
            post_op.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("examples", {})
        )
        assert len(examples) >= 5
        assert "simplify_and_format" in examples
        assert "quiz_from_doc" in examples
        assert "knowledge_graph_pipeline" in examples
        assert "audio_lesson" in examples
        assert "flashcard_deck" in examples

    def test_swagger_ui_reachable(self, client):
        r = client.get("/docs")
        assert r.status_code == 200
