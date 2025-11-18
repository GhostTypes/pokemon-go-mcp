"""Integration tests for Promo Code-related MCP tools."""

import pytest


class TestPromoCodeTools:
    """Integration tests for all promo code-related tools."""

    @pytest.mark.asyncio
    async def test_get_active_promo_codes(self, ensure_test_data, mcp_server):
        """Test get_active_promo_codes tool."""
        from pogo_mcp.promo_codes import register_promo_code_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_promo_code_tools(mock_mcp)

        get_active_promo_codes = captured_tools['get_active_promo_codes']
        result = await get_active_promo_codes()

        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain promo codes header or no codes message
        assert "Promo Code" in result or "promo code" in result or "No" in result
