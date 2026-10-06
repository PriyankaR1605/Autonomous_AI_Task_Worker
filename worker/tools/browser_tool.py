import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from worker.config import settings
from worker.tools.base import BaseTool, ToolResult

class BrowserTool(BaseTool):
    name = "browser_automation"
    description = "Controls a web browser via Playwright to navigate, interact with UI forms, and capture visual proof."

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def _ensure_browser(self):
        if not self.browser or not self.page:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=settings.HEADLESS_BROWSER,
                slow_mo=1000 # 1 full second between actions for clear visual observation
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            self.page = await self.context.new_page()

    async def capture_screenshot(self, label: str = "step") -> str:
        if not self.page:
            return ""
        filename = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
        filepath = os.path.join(settings.SCREENSHOTS_DIR, filename)
        await self.page.screenshot(path=filepath, full_page=True)
        return filepath

    async def execute(self, action: str, **kwargs) -> ToolResult:
        try:
            await self._ensure_browser()

            if action == "navigate":
                url = kwargs.get("url", settings.MOCK_ERP_BASE_URL)
                await self.page.goto(url, wait_until="networkidle")
                shot = await self.capture_screenshot("navigate")
                title = await self.page.title()
                return ToolResult(
                    success=True,
                    output=f"Navigated to '{url}'. Page title: '{title}'.",
                    screenshot_path=shot,
                    data={"url": url, "title": title}
                )

            elif action == "login":
                username = kwargs.get("username", settings.ERP_ADMIN_USER)
                password = kwargs.get("password", settings.ERP_ADMIN_PASS)
                
                # Navigate to login if not already there
                if "/login" not in self.page.url:
                    await self.page.goto(f"{settings.MOCK_ERP_BASE_URL}/login", wait_until="networkidle")

                # Fill credentials with fallback selectors
                await self._fill_with_fallback(["#username", "input[name='username']"], username)
                await self._fill_with_fallback(["#password", "input[name='password']"], password)
                
                # Click submit
                await self._click_with_fallback(["#btn-login", "button[type='submit']"])
                await self.page.wait_for_load_state("networkidle")

                shot = await self.capture_screenshot("after_login")

                # Verify login success by checking if redirected to dashboard
                if "/dashboard" in self.page.url:
                    return ToolResult(
                        success=True,
                        output=f"Successfully authenticated as '{username}' and reached dashboard.",
                        screenshot_path=shot,
                        data={"url": self.page.url}
                    )
                else:
                    return ToolResult(
                        success=False,
                        output=f"Login failed. Remaining at: {self.page.url}",
                        screenshot_path=shot,
                        error="AUTHENTICATION_FAILED"
                    )

            elif action == "navigate_to_new_invoice":
                await self.page.goto(f"{settings.MOCK_ERP_BASE_URL}/invoices/new", wait_until="networkidle")
                shot = await self.capture_screenshot("new_invoice_form")
                return ToolResult(
                    success=True,
                    output="Navigated to invoice creation form.",
                    screenshot_path=shot,
                    data={"url": self.page.url}
                )

            elif action == "submit_invoice":
                vendor_name = kwargs.get("vendor_name", "")
                invoice_number = kwargs.get("invoice_number", "")
                amount = str(kwargs.get("amount", ""))
                due_date = kwargs.get("due_date", "")
                notes = kwargs.get("notes", "Submitted autonomously by AI Worker")

                # Ensure on new invoice page
                if "/invoices/new" not in self.page.url:
                    await self.page.goto(f"{settings.MOCK_ERP_BASE_URL}/invoices/new", wait_until="networkidle")

                # Fill all fields
                await self._fill_with_fallback(["#vendor_name", "input[name='vendor_name']"], vendor_name)
                await self._fill_with_fallback(["#invoice_number", "input[name='invoice_number']"], invoice_number)
                await self._fill_with_fallback(["#amount", "input[name='amount']"], amount)
                await self._fill_with_fallback(["#due_date", "input[name='due_date']"], due_date)
                
                if notes:
                    await self._fill_with_fallback(["#notes", "textarea[name='notes']"], notes)

                # Capture pre-submit screenshot for audit trail
                pre_shot = await self.capture_screenshot("form_filled")

                # Click Submit
                await self._click_with_fallback(["#btn-submit-invoice", "button[type='submit']"])
                await self.page.wait_for_load_state("networkidle")

                post_shot = await self.capture_screenshot("submission_result")

                # Check if submission was successful (redirected to /dashboard?message=...)
                if "/dashboard" in self.page.url:
                    return ToolResult(
                        success=True,
                        output=f"Successfully recorded invoice '{invoice_number}' for '{vendor_name}' in ERP.",
                        screenshot_path=post_shot,
                        data={
                            "pre_submit_screenshot": pre_shot,
                            "post_submit_screenshot": post_shot,
                            "vendor_name": vendor_name,
                            "invoice_number": invoice_number,
                            "amount": amount,
                            "due_date": due_date
                        }
                    )
                else:
                    # Check for error banners
                    err_element = await self.page.query_selector("#form-error-banner")
                    err_msg = await err_element.inner_text() if err_element else "Form submission failed."
                    return ToolResult(
                        success=False,
                        output=f"Form submission error: {err_msg}",
                        screenshot_path=post_shot,
                        error=err_msg
                    )

            elif action == "close":
                await self.close()
                return ToolResult(success=True, output="Browser session closed cleanly.")

            else:
                return ToolResult(
                    success=False,
                    output=f"Unknown browser action: {action}",
                    error="UNKNOWN_ACTION"
                )

        except Exception as e:
            shot = ""
            if self.page:
                try:
                    shot = await self.capture_screenshot("error")
                except Exception:
                    pass
            return ToolResult(
                success=False,
                output=f"Browser automation error: {str(e)}",
                screenshot_path=shot,
                error=str(e)
            )

    async def _fill_with_fallback(self, selectors: list, text: str):
        for sel in selectors:
            try:
                el = await self.page.wait_for_selector(sel, timeout=3000)
                if el:
                    await el.fill(text)
                    return
            except Exception:
                continue
        raise RuntimeError(f"Could not locate any matching element for input among: {selectors}")

    async def _click_with_fallback(self, selectors: list):
        for sel in selectors:
            try:
                el = await self.page.wait_for_selector(sel, timeout=3000)
                if el:
                    await el.click()
                    return
            except Exception:
                continue
        raise RuntimeError(f"Could not locate clickable element among: {selectors}")

    async def close(self):
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        self.page = None
