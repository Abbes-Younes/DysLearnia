"""
tests/test_pipeline_file_endpoint.py

Tests for:
  - POST /api/pipeline/run/file  (multipart: file + pipeline JSON)
  - CourseInputBlock doc_id reload path
  - db.qdrant.get_all_chunks
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import blocks  # noqa: F401
from blocks.base import BlockData


@pytest.fixture(scope="module")
def client():
    with (
        patch("core.graph.build_graph", return_value=MagicMock()),
        patch("models.local_llm.init_llm"),
    ):
        from main import app
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


FAKE_PDF = b"%PDF-1.4 fake"
PIPELINE_QUIZ = json.dumps({
    "nodes": [
        {"id": "n1", "type": "course_input"},
        {"id": "n2", "type": "quiz_builder"},
    ],
    "edges": [{"source": "n1", "target": "n2"}],
    "params": {"n2": {"count": 3}},
})


# ── POST /api/pipeline/run/file ────────────────────────────────────────────────

class TestRunPipelineWithFile:
    def _post(self, client, pipeline_json=PIPELINE_QUIZ, file_bytes=FAKE_PDF,
              filename="lecture.pdf", content_type="application/pdf"):
        return client.post(
            "/api/pipeline/run/file",
            data={"pipeline": pipeline_json},
            files={"file": (filename, file_bytes, content_type)},
        )

    def test_returns_200_with_mocked_blocks(self, client):
        extracted = [BlockData(text="Extracted text", mime_type="text/plain",
                               metadata={"doc_id": "d1", "chunk_count": 2, "page_count": 1})]
        quiz_out = [BlockData(text='[{"q":"Q1"}]', mime_type="application/json")]

        with (
            patch("blocks.inputs.course_input.CourseInputBlock.execute",
                  new=AsyncMock(return_value=extracted)),
            patch("blocks.transform.quiz_builder.QuizBuilderBlock.execute",
                  new=AsyncMock(return_value=quiz_out)),
        ):
            r = self._post(client)

        assert r.status_code == 200
        data = r.json()
        assert data["run_id"] != ""
        assert "n2" in data["outputs"]

    def test_course_input_receives_binary(self, client):
        """Verify the file bytes actually arrive at CourseInputBlock.execute()."""
        captured = []

        async def capture(self_, inputs, params):
            captured.extend(inputs)
            return [BlockData(text="ok", mime_type="text/plain",
                              metadata={"doc_id": "d1", "chunk_count": 1, "page_count": 0})]

        with (
            patch("blocks.inputs.course_input.CourseInputBlock.execute", new=capture),
            patch("blocks.transform.quiz_builder.QuizBuilderBlock.execute",
                  new=AsyncMock(return_value=[BlockData(text="[]")])),
        ):
            self._post(client, file_bytes=b"binary-content")

        assert len(captured) == 1
        assert captured[0].binary == b"binary-content"

    def test_empty_file_returns_400(self, client):
        r = self._post(client, file_bytes=b"")
        assert r.status_code == 400

    def test_invalid_pipeline_json_returns_422(self, client):
        r = self._post(client, pipeline_json="not json at all")
        assert r.status_code == 422

    def test_pipeline_without_course_input_returns_422(self, client):
        pipeline = json.dumps({
            "nodes": [{"id": "n1", "type": "summarizer"}],
            "edges": [],
            "params": {},
        })
        r = self._post(client, pipeline_json=pipeline)
        assert r.status_code == 422
        assert "course_input" in r.json()["detail"].lower()

    def test_course_input_in_middle_not_used_as_source(self, client):
        """A course_input node that HAS incoming edges should not be seeded."""
        pipeline = json.dumps({
            "nodes": [
                {"id": "n1", "type": "summarizer"},  # no course_input source
                {"id": "n2", "type": "course_input"},  # has incoming edge
            ],
            "edges": [{"source": "n1", "target": "n2"}],
            "params": {},
        })
        r = self._post(client, pipeline_json=pipeline)
        # No source course_input nodes → 422
        assert r.status_code == 422

    def test_run_id_is_uuid(self, client):
        import uuid as _uuid
        with (
            patch("blocks.inputs.course_input.CourseInputBlock.execute",
                  new=AsyncMock(return_value=[BlockData(text="t", mime_type="text/plain",
                                                         metadata={"doc_id": "x",
                                                                    "chunk_count": 1,
                                                                    "page_count": 0})])),
            patch("blocks.transform.quiz_builder.QuizBuilderBlock.execute",
                  new=AsyncMock(return_value=[BlockData(text="[]")])),
        ):
            r = self._post(client)
        _uuid.UUID(r.json()["run_id"])

    def test_three_node_pipeline_full_chain(self, client):
        pipeline = json.dumps({
            "nodes": [
                {"id": "n1", "type": "course_input"},
                {"id": "n2", "type": "summarizer"},
                {"id": "n3", "type": "knowledge_graph"},
            ],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"},
            ],
            "params": {},
        })
        n1_out = [BlockData(text="doc text", mime_type="text/plain",
                            metadata={"doc_id": "d1", "chunk_count": 1, "page_count": 0})]
        n2_out = [BlockData(text="summary", mime_type="text/plain")]
        n3_out = [BlockData(text='{"nodes":[],"links":[]}', mime_type="application/json",
                            metadata={"doc_id": "d1"})]

        with (
            patch("blocks.inputs.course_input.CourseInputBlock.execute",
                  new=AsyncMock(return_value=n1_out)),
            patch("blocks.transform.summarizer.SummarizerBlock.execute",
                  new=AsyncMock(return_value=n2_out)),
            patch("blocks.transform.knowledge_graph.KnowledgeGraphBlock.execute",
                  new=AsyncMock(return_value=n3_out)),
        ):
            r = client.post(
                "/api/pipeline/run/file",
                data={"pipeline": pipeline},
                files={"file": ("slides.pdf", FAKE_PDF, "application/pdf")},
            )

        assert r.status_code == 200
        assert "n3" in r.json()["outputs"]


# ── CourseInputBlock — doc_id reload path ────────────────────────────────────

class TestCourseInputDocIdPath:
    @pytest.mark.asyncio
    async def test_reloads_chunks_from_qdrant(self):
        from blocks.inputs.course_input import CourseInputBlock

        block = CourseInputBlock()
        chunks = ["Chunk one.", "Chunk two.", "Chunk three."]

        with patch("db.qdrant.get_all_chunks", return_value=chunks):
            result = await block.execute([], {"doc_id": "test-doc"})

        assert len(result) == 1
        bd = result[0]
        assert "Chunk one." in bd.text
        assert "Chunk two." in bd.text
        assert bd.metadata["doc_id"] == "test-doc"
        assert bd.metadata["chunk_count"] == 3

    @pytest.mark.asyncio
    async def test_empty_chunks_returns_error(self):
        from blocks.inputs.course_input import CourseInputBlock

        block = CourseInputBlock()
        with patch("db.qdrant.get_all_chunks", return_value=[]):
            result = await block.execute([], {"doc_id": "missing-doc"})

        assert "error" in result[0].metadata

    @pytest.mark.asyncio
    async def test_no_binary_no_doc_id_returns_error(self):
        from blocks.inputs.course_input import CourseInputBlock

        result = await CourseInputBlock().execute([], {})
        assert "error" in result[0].metadata

    @pytest.mark.asyncio
    async def test_binary_path_still_works(self):
        """Providing binary input ignores the doc_id path."""
        from blocks.inputs.course_input import CourseInputBlock

        block = CourseInputBlock()
        bd_in = BlockData(binary=FAKE_PDF, mime_type="application/pdf",
                          metadata={"user_id": "u1"})

        # The fake PDF won't parse but we just check the binary path is entered
        with patch.object(block, "_extract_pdf", return_value=("Extracted text", [])):
            with patch("db.qdrant.index_document", return_value=True):
                result = await block.execute([bd_in], {})

        assert result[0].text == "Extracted text"

    @pytest.mark.asyncio
    async def test_doc_id_param_ignored_when_binary_provided(self):
        """When binary IS present, doc_id param should not trigger Qdrant reload."""
        from blocks.inputs.course_input import CourseInputBlock

        block = CourseInputBlock()
        bd_in = BlockData(binary=FAKE_PDF, mime_type="application/pdf")

        reload_called = []

        def fake_get_chunks(doc_id):
            reload_called.append(doc_id)
            return ["chunk"]

        with (
            patch("db.qdrant.get_all_chunks", side_effect=fake_get_chunks),
            patch.object(block, "_extract_pdf", return_value=("text", [])),
            patch("db.qdrant.index_document", return_value=True),
        ):
            await block.execute([bd_in], {"doc_id": "should-be-ignored"})

        assert reload_called == []  # binary path taken, Qdrant reload NOT called


# ── db.qdrant.get_all_chunks (unit — no real Qdrant) ─────────────────────────

class TestGetAllChunksUnit:
    def test_returns_empty_when_no_client(self):
        from db import qdrant as q
        original = q._client
        q._client = None
        try:
            import os
            orig_url = os.environ.pop("QDRANT_URL", None)
            result = q.get_all_chunks("any-doc")
            assert result == []
        finally:
            q._client = original
            if orig_url:
                os.environ["QDRANT_URL"] = orig_url

    def test_scrolls_until_offset_none(self):
        """Verify the scroll loop terminates and collects all pages."""
        from db import qdrant as q

        page1 = [
            MagicMock(payload={"text": f"chunk{i}", "chunk_index": i}) for i in range(3)
        ]
        page2 = [
            MagicMock(payload={"text": f"chunk{i}", "chunk_index": i}) for i in range(3, 5)
        ]

        mock_client = MagicMock()
        mock_client.scroll.side_effect = [
            (page1, "cursor-1"),  # first call returns cursor
            (page2, None),        # second call signals end
        ]

        original = q._client
        q._client = mock_client
        try:
            result = q.get_all_chunks("doc-123")
        finally:
            q._client = original

        assert mock_client.scroll.call_count == 2
        assert result == [f"chunk{i}" for i in range(5)]

    def test_single_page_terminates_immediately(self):
        from db import qdrant as q

        records = [MagicMock(payload={"text": "only chunk", "chunk_index": 0})]
        mock_client = MagicMock()
        mock_client.scroll.return_value = (records, None)

        original = q._client
        q._client = mock_client
        try:
            result = q.get_all_chunks("doc-x")
        finally:
            q._client = original

        assert mock_client.scroll.call_count == 1
        assert result == ["only chunk"]


# ── POST /api/pipeline/run — doc_id flow via JSON endpoint ────────────────────

class TestRunPipelineDocIdFlow:
    """Flow A: upload already done, use doc_id param in course_input."""

    def test_doc_id_flow_end_to_end(self, client):
        reloaded = [BlockData(text="Full doc text from Qdrant", mime_type="text/plain",
                              metadata={"doc_id": "my-doc", "chunk_count": 5})]
        quiz_out = [BlockData(text='[{"q":"Q1","a":"A1"}]', mime_type="application/json")]

        with (
            patch("blocks.inputs.course_input.CourseInputBlock.execute",
                  new=AsyncMock(return_value=reloaded)),
            patch("blocks.transform.quiz_builder.QuizBuilderBlock.execute",
                  new=AsyncMock(return_value=quiz_out)),
        ):
            r = client.post("/api/pipeline/run", json={
                "nodes": [
                    {"id": "n1", "type": "course_input"},
                    {"id": "n2", "type": "quiz_builder"},
                ],
                "edges": [{"source": "n1", "target": "n2"}],
                "params": {"n1": {"doc_id": "my-doc"}, "n2": {"count": 3}},
                "initial_inputs": {},
            })

        assert r.status_code == 200
        outputs = r.json()["outputs"]
        assert "n2" in outputs
        assert "Q1" in outputs["n2"][0]["text"]
