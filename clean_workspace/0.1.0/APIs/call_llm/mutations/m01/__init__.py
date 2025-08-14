from .llm_execution import create_generative_text, invoke_model_with_tool_support, parse_docstring_to_tool_object

_function_map = {
    'create_generative_text': 'call_llm.mutations.m01.llm_execution.create_generative_text',
    'invoke_model_with_tool_support': 'call_llm.mutations.m01.llm_execution.invoke_model_with_tool_support',
    'parse_docstring_to_tool_object': 'call_llm.mutations.m01.llm_execution.parse_docstring_to_tool_object',
}
