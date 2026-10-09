import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from worker.config import settings
from worker.tools.base import BaseTool, ToolResult

class FileSearchTool(BaseTool):
    name = "file_search"
    description = "Searches the enterprise repository for documents, invoices, policies, and contracts."

    async def execute(
        self, 
        query: Optional[str] = None, 
        vendor_name: Optional[str] = None, 
        folder: Optional[str] = None,
        find_latest: bool = True
    ) -> ToolResult:
        try:
            search_dirs = []
            if folder:
                custom_dir = os.path.join(settings.DATA_DIR, folder) if not os.path.isabs(folder) else folder
                if os.path.exists(custom_dir):
                    search_dirs.append(custom_dir)
            else:
                # Default search across all data repositories
                docs_dir = os.path.join(settings.DATA_DIR, "company_docs")
                invoices_dir = settings.INVOICES_DIR
                tables_dir = getattr(settings, "TABLES_DIR", os.path.join(settings.DATA_DIR, "enterprise_tables"))
                if os.path.exists(invoices_dir):
                    search_dirs.append(invoices_dir)
                if os.path.exists(docs_dir):
                    search_dirs.append(docs_dir)
                if os.path.exists(tables_dir):
                    search_dirs.append(tables_dir)

            if not search_dirs:
                return ToolResult(
                    success=False,
                    output="No document repository directories found.",
                    error="DIRECTORY_NOT_FOUND"
                )

            term = query or vendor_name or ""
            clean_term = re.sub(r'[^a-zA-Z0-9]', '', term.lower()) if term else ""

            matched_files = []

            for s_dir in search_dirs:
                for root, _, files in os.walk(s_dir):
                    for filename in files:
                        if not (filename.endswith(".pdf") or filename.endswith(".txt") or filename.endswith(".md") or filename.endswith(".csv") or filename.endswith(".json")):
                            continue

                        clean_fname = re.sub(r'[^a-zA-Z0-9]', '', filename.lower())
                        
                        # Match condition
                        if not clean_term or (clean_term in clean_fname):
                            filepath = os.path.join(root, filename)
                            stat = os.stat(filepath)
                            mtime = datetime.fromtimestamp(stat.st_mtime)
                            
                            score = 50
                            if "latest" in filename.lower():
                                score += 50
                            if clean_term and clean_term in clean_fname:
                                score += 30
                            if filename.endswith(".pdf"):
                                score += 10 # Prefer PDF over text companion

                            matched_files.append({
                                "filename": filename,
                                "filepath": filepath,
                                "directory": os.path.basename(root),
                                "size_bytes": stat.st_size,
                                "modified_at": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                                "priority_score": score
                            })

            if not matched_files:
                return ToolResult(
                    success=False,
                    output=f"No enterprise files found matching '{term}' in {search_dirs}.",
                    error="NO_FILES_FOUND"
                )

            # Sort by priority score first, then by modified timestamp descending
            matched_files.sort(key=lambda x: (x["priority_score"], x["modified_at"]), reverse=True)

            if find_latest:
                latest = matched_files[0]
                return ToolResult(
                    success=True,
                    output=f"Located target file for '{term}': {latest['filename']} (Path: {latest['filepath']})",
                    data={
                        "latest_file": latest,
                        "all_matches": matched_files,
                        "count": len(matched_files)
                    }
                )

            return ToolResult(
                success=True,
                output=f"Found {len(matched_files)} matching files for '{term}'.",
                data={"matches": matched_files, "count": len(matched_files)}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Failed to search enterprise files: {str(e)}",
                error=str(e)
            )
