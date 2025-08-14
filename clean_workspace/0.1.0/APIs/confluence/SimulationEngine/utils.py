# APIs/confluence/SimulationEngine/utils.py
import re
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, Union


def get_iso_timestamp() -> str:
    """
    Returns current UTC time in ISO 8601 format with 'Z' suffix.
    Formats the timestamp to exactly 3 decimal places for milliseconds.
    
    Returns:
        str: Current UTC timestamp in format: YYYY-MM-DDTHH:mm:ss.sssZ
    """
    # Use timezone-aware datetime with UTC
    dt = datetime.now(UTC)
    # Format with exactly 3 decimal places
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def _evaluate_cql_expression(content: Dict[str, Any], expression: str) -> bool:
    """Evaluates a single CQL expression against a content item.

    Args:
        content (Dict[str, Any]): The content item to evaluate against.
        expression (str): The CQL expression to evaluate (e.g., "type='page'").

    Returns:
        bool: True if the content matches the expression, False otherwise.
    """
    # Regex to capture field, operator, and value (handling both quote types for value)
    # MODIFIED: Correctly captures value regardless of quote type into separate groups.
    # Field names can be simple words.
    # Operator can be one of =, !=, >, <, >=, <=, ~, !~
    # Value is enclosed in single or double quotes.
    match = re.match(
        r"(\w+)\s*([>=<!~]+)\s*(?:'([^']*)'|\"([^\"]*)\")", expression, re.IGNORECASE
    )

    if not match:
        # This can happen if a token is not a valid expression (e.g. a standalone operator passed incorrectly)
        # Or if the expression is malformed.
        # print(f"DEBUG: No match for expression: '{expression}'") # For debugging
        return False

    groups = match.groups()
    field = groups[0].lower() # Normalize field name to lower for case-insensitive matching if desired
    operator = groups[1]
    
    # The value will be in either groups[2] (single_quoted_value) or groups[3] (double_quoted_value)
    # One of them will be None, the other will have the string value.
    single_quoted_value = groups[2]
    double_quoted_value = groups[3]

    value = single_quoted_value if single_quoted_value is not None else double_quoted_value
    
    # Normalize field access: try common variations if direct match fails
    # For example, Confluence might use 'spaceKey' but user might type 'space'.
    # This example uses exact field names from DB structure.
    # For more robustness, you might want to map aliases or try case variations.
    content_value = None
    if field in content:
        content_value = content[field]
    elif field.lower() in content: # try lowercase field name
         content_value = content[field.lower()]
    else: # Try to find a key that matches case-insensitively
        for k in content.keys():
            if k.lower() == field:
                content_value = content[k]
                break
    
    # If field is not found in content, it cannot match
    # (unless operator is '!=' and value is something specific, but CQL usually implies field presence)
    # For robust CQL, if a field doesn't exist, comparisons like '=' should be false.
    # Comparisons like '!=' could be true if the field is absent and value is not None-like.
    # Current Confluence behavior: if a field doesn't exist, it's treated as null.
    # So, 'nonExistentField = "someValue"' is false. 'nonExistentField != "someValue"' is true.
    # 'nonExistentField = empty' might be true.

    if content_value is None: # Field does not exist in content
        if operator == "!=": # field != value -> true if field is null
            return True
        elif operator == "!~": # field !~ value -> true if field is null
             return True
        return False # For =, >, <, >=, <=, ~ if field is null, it's generally false

    # Convert content_value to string for comparison, unless numeric comparison is needed
    # For operators like ~, !~, =, != (when value is not explicitly numeric), string comparison is typical.
    # For >, <, >=, <=, numeric comparison is typical if possible.

    if operator == "=":
        return str(content_value).lower() == str(value).lower() # Case-insensitive string comparison
    elif operator == "!=":
        return str(content_value).lower() != str(value).lower() # Case-insensitive
    elif operator in (">", ">=", "<", "<="):
        try:
            # Attempt numeric comparison
            num_content_value = float(str(content_value)) # Ensure content_value is treated as string first if it's not number
            num_value = float(value)
            if operator == ">": return num_content_value > num_value
            if operator == ">=": return num_content_value >= num_value
            if operator == "<": return num_content_value < num_value
            if operator == "<=": return num_content_value <= num_value
        except (ValueError, TypeError):
            # If conversion to float fails, treat as string comparison or return False
            # Confluence CQL might return error or specific behavior.
            # For simplicity, if numeric comparison fails, consider it a non-match for these ops.
            return False
    elif operator == "~": # Contains
        return str(value).lower() in str(content_value).lower() # Case-insensitive
    elif operator == "!~": # Does not contain
        return str(value).lower() not in str(content_value).lower() # Case-insensitive

    return False


def _evaluate_cql_tree(content: Dict[str, Any], tokens: List[str]) -> bool:
    """
    Evaluates a list of CQL tokens (in infix order) against a content item,
    handling parentheses and logical operators (AND, OR, NOT) using
    a standard shunting-yard-like approach for operator precedence.

    Args:
        content (Dict[str, Any]): The content item to evaluate against.
        tokens (List[str]): List of CQL tokens (expressions, operators, parentheses).

    Returns:
        bool: True if the content matches the CQL expression tree, False otherwise.
    
    Raises:
        ValueError: If the token expression is malformed (e.g. mismatched parentheses).
    """
    if not tokens:
        return True # An empty query could mean "match all" or "match none".
                     # Confluence usually returns all if CQL is empty.
                     # search_content handles empty cql string separately.
                     # If _evaluate_cql_tree is called with empty tokens (e.g. from a sub-expression),
                     # it should ideally not happen if tokenizer is robust.
                     # Let's assume for a sub-expression, empty tokens means true (neutral element for AND, absorbing for OR if not careful)
                     # For safety, let's make it false if called directly with no tokens.
                     # The main function `search_content` should handle an initially empty `cql` string.
                     # If `tokens` is empty here, it implies a parsing issue or an empty sub-expression.
                     # Let's make it strict: if tokens are empty, it's a non-match.
        return False


    # Operator precedence and associativity
    precedence = {"not": 3, "and": 2, "or": 1, "(": 0} # Lower numbers for grouping like '('
    # 'not' is right-associative, 'and'/'or' are left-associative.

    output_queue = []  # For RPN (Reverse Polish Notation)
    operator_stack = []

    # Shunting-yard algorithm to convert infix tokens to RPN
    for token in tokens:
        token_lower = token.lower() # Normalize operators
        if token_lower not in precedence and token_lower not in ("(", ")"): # It's an operand (expression)
            output_queue.append(token) # Keep original case for expression evaluation
        elif token_lower == "(":
            operator_stack.append(token_lower)
        elif token_lower == ")":
            while operator_stack and operator_stack[-1] != "(":
                output_queue.append(operator_stack.pop())
            if not operator_stack or operator_stack[-1] != "(":
                raise ValueError("Mismatched parentheses in CQL query")
            operator_stack.pop()  # Pop "("
        else: # It's an operator (and, or, not)
            # For 'not' (right-associative), we don't pop operators of same precedence.
            # For 'and', 'or' (left-associative), we pop operators of same or higher precedence.
            while (operator_stack and operator_stack[-1] != "(" and
                   (precedence[operator_stack[-1]] > precedence[token_lower] or
                    (precedence[operator_stack[-1]] == precedence[token_lower] and token_lower != "not"))):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token_lower)

    while operator_stack:
        if operator_stack[-1] == "(":
            raise ValueError("Mismatched parentheses in CQL query")
        output_queue.append(operator_stack.pop())

    # Evaluate the RPN expression
    eval_stack = []
    for token in output_queue:
        token_lower = token.lower() # For checking operators
        if token_lower == "and":
            if len(eval_stack) < 2: raise ValueError("Invalid CQL syntax for AND")
            right = eval_stack.pop()
            left = eval_stack.pop()
            eval_stack.append(left and right)
        elif token_lower == "or":
            if len(eval_stack) < 2: raise ValueError("Invalid CQL syntax for OR")
            right = eval_stack.pop()
            left = eval_stack.pop()
            eval_stack.append(left or right)
        elif token_lower == "not":
            if len(eval_stack) < 1: raise ValueError("Invalid CQL syntax for NOT")
            operand = eval_stack.pop()
            eval_stack.append(not operand)
        else: # It's an operand (an expression string like "type='page'")
            eval_stack.append(_evaluate_cql_expression(content, token))
            
    if len(eval_stack) == 1:
        return eval_stack[0]
    elif not eval_stack and not output_queue: # Original tokens were empty, and output_queue is empty
        return True # No conditions to check, so true
    elif not eval_stack and output_queue: # Should not happen if RPN is valid
         raise ValueError("Invalid CQL structure leading to empty evaluation stack")
    else: # Should not happen if RPN is valid and evaluated correctly
        raise ValueError("Invalid CQL structure - multiple values left on stack")

def _collect_descendants(
    content: Dict[str, Any], target_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Helper function to recursively collect descendants of a content item.

    Args:
        content (Dict[str, Any]): The content item to start collecting from
        target_type (Optional[str]): If specified, only collect descendants of this type.
            If None, collect all descendants.

    Returns:
        List[Dict[str, Any]]: List of descendant content items
    """
    descendants = []
    children = content.get("children", [])
    for child in children:
        if child:
            if target_type is None or child.get("type") == target_type:
                descendants.append(child)
            # Recursively collect descendants of this child
            descendants.extend(_collect_descendants(child, target_type))
    return descendants
