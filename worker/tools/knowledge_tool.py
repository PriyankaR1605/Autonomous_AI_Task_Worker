import os
import re
from typing import Optional, Dict, Any, List
from worker.config import settings
from worker.tools.base import BaseTool, ToolResult
from mock_erp.database import search_knowledge_base

class KnowledgeBaseTool(BaseTool):
    name = "knowledge_search"
    description = (
        "Searches company policies, governance rules, employee handbook, "
        "procurement thresholds, IT security regulations, and vendor contracts."
    )

    async def execute(self, query: str) -> ToolResult:
        try:
            q = query.strip().lower()
            kb_results = search_knowledge_base(q)
            
            # Also check text files in company_docs
            docs_dir = os.path.join(settings.DATA_DIR, "company_docs")
            file_excerpts = []
            
            if os.path.exists(docs_dir):
                for fname in os.listdir(docs_dir):
                    if fname.endswith(".txt"):
                        fpath = os.path.join(docs_dir, fname)
                        with open(fpath, "r", encoding="utf-8") as f:
                            text = f.read()
                            if q in text.lower():
                                # Extract matching lines
                                matches = [l.strip() for l in text.splitlines() if q in l.lower()][:3]
                                file_excerpts.append({
                                    "file": fname,
                                    "excerpts": matches
                                })

            output_lines = [f"Found {len(kb_results)} policy knowledge entries and {len(file_excerpts)} document references for '{query}':"]
            for kb in kb_results:
                output_lines.append(f"- [{kb['category']}] {kb['title']}: {kb['summary']} (File: {kb['file_path']})")
            for f in file_excerpts:
                output_lines.append(f"- From document '{f['file']}': " + " | ".join(f['excerpts']))

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
                data={"kb_results": kb_results, "file_excerpts": file_excerpts}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Knowledge base search error: {str(e)}",
                error=str(e)
            )
