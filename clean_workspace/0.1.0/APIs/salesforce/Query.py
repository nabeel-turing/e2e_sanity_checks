# APIs/salesforce/Query.py
from typing import  List, Tuple, Dict, Any
import urllib.parse
from salesforce.SimulationEngine.db import DB


def get(q: str) -> Dict[str, Any]:
    """
    Executes a SOQL-like query against the in-memory database.

    The query string is first URL-decoded. 
    The parser has specific behaviors and improved parsing logic as detailed below.

    Args:
        q (str): The SOQL-like query string. Example:
                 "SELECT Name, Location FROM Event WHERE Location = 'Boardroom' ORDER BY Name ASC OFFSET 0 LIMIT 5"

    Returns:
        Dict[str, Any]: Query results with structure:
            - results (list): List of matching records (dictionaries).
            - error (str): Error message if the query is malformed/fails.

    Raises:
        ValueError: If the query is fundamentally malformed (e.g., missing SELECT or FROM clause).

    Notes:
        Supported Clauses & Parsing Behaviors:
        --------------------------------------
        SELECT <field1[, field2...]>
            - Purpose: Specifies fields to retrieve.
            - Keyword 'SELECT': Case-insensitive.
            - Fields: Comma-separated if multiple. All specified fields are now reliably selected.
            The parser correctly identifies fields listed between SELECT and FROM.

        FROM <ObjectName>
            - Purpose: Specifies the object to query (e.g., "FROM Event").
            - Keyword 'FROM': MUST be UPPERCASE.

        WHERE <conditions>
            - Purpose: Filters records based on conditions.
            - Keywords 'WHERE', 'AND': MUST be UPPERCASE.
            - Conditions: Multiple conditions are combined with 'AND'.
            - Operators: '=', '>', '<'. (Note: The `parse_conditions` helper function defines more operators
            like 'IN', 'LIKE', 'CONTAINS', but the main `get` function currently only implements direct
            logic for '=', '>', '<' in its record filtering loop).
            - String Literals: Must be enclosed in single or double quotes (e.g., "Name = 'Test Value'").
            - Parsing: The WHERE condition string is now parsed to correctly end before other major clauses
            like 'ORDER BY', 'LIMIT', or 'OFFSET'. This prevents tokens from these clauses from being
            incorrectly included in the WHERE condition.

        ORDER BY <field> [ASC|DESC]
            - Purpose: Sorts the results.
            - Keywords 'ORDER BY', 'ASC', 'DESC': MUST be UPPERCASE. 'ASC' is default.
            - Behavior: Sorting by <field> works correctly if <field> is selected (i.e., present in the
            records after the SELECT phase). If the <field> to sort by is not present in the
            records being sorted (e.g., not selected, or does not exist on records), the sort key
            becomes an empty string for those items, potentially resulting in an unstable sort
            (often preserving the original retrieval order for those items relative to each other).

        OFFSET <number>
            - Purpose: Skips a specified number of records from the beginning of the result set *after sorting*.
            - Keyword 'OFFSET': MUST be UPPERCASE.
            - Interaction with LIMIT: OFFSET is applied to the result set first, then LIMIT is applied.
            The order of OFFSET and LIMIT keywords in the query string does not affect this execution sequence.
            The internal logic first applies OFFSET to the sorted list, then LIMIT to that offsetted list.

        LIMIT <number>
            - Purpose: Restricts the number of records returned *after sorting and offsetting*.
            - Keyword 'LIMIT': MUST be UPPERCASE.
    """
    if not isinstance(q, str):
        raise TypeError("Argument 'q' must be a string.")

    try:
        # Decode URL-encoded query
        q = urllib.parse.unquote(q)
        parts = q.split()

        if parts[0].upper() != "SELECT":
            raise ValueError("Invalid SOQL query: Must start with SELECT")

        # Object to query (determine from_index first for robust field parsing)
        from_index = -1
        # Find FROM keyword considering it might not be in 'parts' if query is malformed before FROM
        temp_q_parts = q.split() # Use a fresh split of q to reliably find FROM's original position
        for i, part in enumerate(temp_q_parts):
            if part.upper() == "FROM":
                from_index = i # This index is relative to temp_q_parts
                break
        
        if from_index == -1 or from_index == 0: # from_index == 0 means SELECT is missing or FROM is first
             # Try to find FROM in the original 'parts' as a fallback if temp_q_parts logic is insufficient or query is very short
            if "FROM" in parts:
                from_index = parts.index("FROM")
            else:
                raise ValueError("Invalid SOQL query: Missing FROM clause or malformed structure")

        # Fields to select
        # Use 'parts' for field string construction as 'parts' is what's used for subsequent parsing
        # Ensure from_index used for slicing 'parts' is valid for 'parts' list length
        actual_from_index_in_parts = parts.index("FROM") if "FROM" in parts else -1
        if actual_from_index_in_parts <= 0 : # Must be at least after SELECT (parts[0])
            raise ValueError("Invalid SOQL query: FROM clause misplaced or missing")

        fields_string = " ".join(parts[1:actual_from_index_in_parts])
        fields = [field.strip() for field in fields_string.split(",") if field.strip()]


        # Object to query
        obj = parts[actual_from_index_in_parts + 1]

        # Initialize variables for conditions, limit, offset, and order_by
        where_index = -1
        limit = None
        offset = None
        order_by = None
        conditions = []

        # Extract WHERE clause conditions
        if "WHERE" in parts:
            where_index = parts.index("WHERE")
            # Determine the end of the WHERE clause
            end_where_index = len(parts)
            # Find the start of the next major clause to delimit WHERE
            for i in range(where_index + 1, len(parts)):
                # Check if the current part is a keyword that terminates a WHERE clause
                # ORDER BY is two words, so check parts[i] and parts[i+1]
                if parts[i].upper() == "ORDER" and i + 1 < len(parts) and parts[i+1].upper() == "BY":
                    end_where_index = i
                    break
                elif parts[i].upper() in ["LIMIT", "OFFSET"]:
                    end_where_index = i
                    break
            
            condition_string = " ".join(parts[where_index + 1 : end_where_index])
            conditions = [c.strip() for c in condition_string.split("AND") if c.strip()]

        # Extract LIMIT clause
        if "LIMIT" in parts:
            limit_index = parts.index("LIMIT")
            limit = int(parts[limit_index + 1])
            #parts = parts[:limit_index]  # Remove LIMIT part from the query

        # Extract OFFSET clause
        if "OFFSET" in parts:
            offset_index = parts.index("OFFSET")
            offset = int(parts[offset_index + 1])
            #parts = parts[:offset_index]  # Remove OFFSET part from the query

        # Extract ORDER BY clause
        if "ORDER BY" in q:
            order_by_index = q.index("ORDER BY")
            order_by = q[order_by_index + 9 :].strip()  # 9 is length of "ORDER BY "
            if "LIMIT" in order_by:
                order_by = order_by[: order_by.index("LIMIT")].strip()
            if "OFFSET" in order_by:
                order_by = order_by[: order_by.index("OFFSET")].strip()

        # Get the appropriate database collection
        if obj not in DB:
            return {"error": f"Object {obj} not found in database"}

        # Apply conditions
        results = []
        for record in DB[obj].values():
            match = True
            for condition in conditions:
                if not condition.strip():
                    continue
                # Simple condition parsing - can be enhanced for more complex conditions
                if "=" in condition:
                    field, value = condition.split("=")
                    field = field.strip()
                    value = value.strip().strip("'").strip('"')
                    if field not in record or str(record[field]) != value:
                        match = False
                        break
                elif ">" in condition:
                    field, value = condition.split(">")
                    field = field.strip()
                    value = value.strip().strip("'").strip('"')
                    if field not in record or not (str(record[field]) > value):
                        match = False
                        break
                elif "<" in condition:
                    field, value = condition.split("<")
                    field = field.strip()
                    value = value.strip().strip("'").strip('"')
                    if field not in record or not (str(record[field]) < value):
                        match = False
                        break

            if match:
                # Select only requested fields
                filtered_record = {}
                for field in fields:
                    if field in record:
                        filtered_record[field] = record[field]
                results.append(filtered_record)

        # Apply ORDER BY
        if order_by:
            field, direction = order_by.split()
            field = field.strip()
            direction = direction.strip().upper()
            results.sort(key=lambda x: x.get(field, ""), reverse=(direction == "DESC"))

        # Apply OFFSET and LIMIT
        if offset is not None:
            results = results[offset:]
        if limit is not None:
            results = results[:limit]

        return {"results": results}

    except Exception as e:
        return {"error": f"Error executing query: {str(e)}"}

def parse_conditions(conditions: List[str]) -> List[Tuple[str, str, str | List[str]]]:
    """
    Parse the conditions in the WHERE clause.
    Handles '=', 'IN', 'LIKE', and 'CONTAINS'.

    Args:
        conditions (List[str]): List of condition strings to parse. Example:
            - "Subject = 'Meeting'"
            - "IsAllDayEvent = true"
            - "Location IN ('Boardroom', 'Conference Room')"
            - "Description LIKE '%important%'"
            - "Subject CONTAINS 'review'"

    Returns:
        List[Tuple[str, str, str | List[str]]]: List of tuples containing (condition_type, field, value) where:
            - condition_type (str): One of '=', 'IN', 'LIKE', 'CONTAINS'
            - field (str): The field name to check
            - value (str | List[str]): The value(s) to compare against
    """
    parsed_conditions = []
    for cond in conditions:
        cond = cond.strip()

        # Handle equality condition
        if "=" in cond:
            field, value = cond.split("=", 1)
            field = field.strip()
            value = value.strip().strip("'")
            parsed_conditions.append(("=", field, value))

        # Handle IN condition
        elif "IN" in cond:
            field, values = cond.split("IN", 1)
            field = field.strip()
            values = values.strip("()").split(",")
            values = [v.strip().strip("'") for v in values]
            parsed_conditions.append(("IN", field, values))

        # Handle LIKE condition
        elif "LIKE" in cond:
            field, value = cond.split("LIKE", 1)
            field = field.strip()
            value = value.strip().strip("'").replace("%", "")
            parsed_conditions.append(("LIKE", field, value))

        # Handle CONTAINS condition
        elif "CONTAINS" in cond:
            field, value = cond.split("CONTAINS", 1)
            field = field.strip()
            value = value.strip().strip("'")
            parsed_conditions.append(("CONTAINS", field, value))

    return parsed_conditions
