"""
MCP Server Integration Tests Template

Copy this file to your tests/ directory and customize:
1. Update tool names and expected behaviors
2. Add test cases for your specific tools
3. Replace placeholder assertions with real validations
"""

import pytest
from fastmcp import Client


class TestToolDiscovery:
    """Verify all expected tools are registered and discoverable."""

    async def test_lists_all_expected_tools(
        self, client: Client, expected_tools: list[str]
    ):
        """All expected tools should appear in tools/list."""
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]

        for expected in expected_tools:
            assert expected in tool_names, f"Expected tool '{expected}' not found"

    async def test_tools_have_descriptions(self, client: Client):
        """Each tool should have a non-empty description."""
        tools = await client.list_tools()

        for tool in tools:
            assert tool.description, f"Tool '{tool.name}' has no description"
            assert len(tool.description) > 10, (
                f"Tool '{tool.name}' description too short"
            )


class TestExampleTool:
    """
    Tests for example_tool_1.

    TODO: Rename this class and customize tests for your actual tools.
    """



    async def test_basic_execution(self, client: Client):
        """Tool executes successfully with valid input."""
        result = await client.call_tool(
            name="example_tool_1",
            arguments={
                # TODO: Add your tool's expected arguments  # noqa: TD002, TD003
                "param1": "value1",
            },
        )

        # TODO: Update assertion to match your tool's expected output  # noqa: TD002, TD003
        assert result.content[0].text is not None

    async def test_handles_missing_required_param(self, client: Client):
        """Tool returns error when required parameter is missing."""
        result = await client.call_tool(
            name="example_tool_1",
            arguments={},  # Missing required params
        )

        # Should indicate an error
        assert result.is_error or "error" in result.content[0].text.lower()

    @pytest.mark.parametrize(
        ("input_val", "expected_output"),
        [
            # TODO: Add test cases with (input, expected_output) pairs  # noqa: TD002, TD003
            ("input1", "output1"),
            ("input2", "output2"),
        ],
    )
    async def test_various_inputs(
        self, client: Client, input_val: str, expected_output: str
    ):
        """Tool handles various inputs correctly."""
        result = await client.call_tool(
            name="example_tool_1", arguments={"param1": input_val}
        )

        assert result.content[0].text == expected_output


class TestErrorHandling:
    """Verify tools handle errors gracefully."""

    async def test_invalid_tool_name(self, client: Client):
        """Calling non-existent tool returns appropriate error."""
        result = await client.call_tool(name="nonexistent_tool_xyz", arguments={})

        assert result.is_error

    async def test_error_messages_are_actionable(self, client: Client):
        """
        Error messages should tell the user what went wrong
        and ideally how to fix it.
        """
        # TODO: Trigger an error in one of your tools  # noqa: TD002, TD003
        result = await client.call_tool(
            name="example_tool_1",
            arguments={"param1": "invalid_value_that_causes_error"},
        )

        if result.is_error:
            error_text = result.content[0].text.lower()
            # Error should be descriptive, not just "error"
            assert len(error_text) > 10


# Optional: Resource tests (if your server exposes resources)
class TestResources:
    """Test resource exposure and retrieval."""

    async def test_lists_resources(self, client: Client, expected_resources: list[str]):
        """All expected resources should be listed."""
        if not expected_resources:
            pytest.skip("No resources expected")

        resources = await client.list_resources()
        resource_uris = [r.uri for r in resources]

        for expected in expected_resources:
            assert expected in resource_uris


# Optional: Prompt tests (if your server exposes prompts)
class TestPrompts:
    """Test prompt exposure and retrieval."""

    async def test_lists_prompts(self, client: Client, expected_prompts: list[str]):
        """All expected prompts should be listed."""
        if not expected_prompts:
            pytest.skip("No prompts expected")

        prompts = await client.list_prompts()
        prompt_names = [p.name for p in prompts]

        for expected in expected_prompts:
            assert expected in prompt_names
