from common_utils.print_log import print_log
# APIs/google_chat/Spaces/Messages/Reactions.py

import sys
import os
from typing import Any, Dict

sys.path.append("APIs")

from google_chat.SimulationEngine.db import DB


def create(parent: str, reaction: dict) -> Dict[str, Any]:
    """
    Creates a reaction and adds it to a message.

    Args:
        parent (str): Required. Resource name of the message to which the reaction is added.
            Format: "spaces/{space}/messages/{message}"
        reaction (dict): Required. The Reaction resource to create with fields:
            - emoji (dict):
                - unicode (str): Optional. A basic emoji represented by a unicode string.
                - customEmoji (dict):
                    - name (str): Identifier. Format: customEmojis/{customEmoji}
                    - uid (str): Output only. Unique key for the custom emoji.
                    - emojiName (str): Optional. User-defined emoji name, must be valid format.
                    - temporaryImageUri (str): Output only. Temporary image URL.
                    - payload (dict):
                        - fileContent (str): Required. Image binary data.
                        - filename (str): Required. Image file name (.png, .jpg, .gif).
            - user (dict):
                - name (str): Required. Format: users/{user}
                - displayName (str): Output only. User's display name.
                - domainId (str): Output only. Workspace domain ID.
                - type (str): Enum: TYPE_UNSPECIFIED, HUMAN, BOT
                - isAnonymous (bool): Output only. True if user is deleted or hidden.

    Returns:
        Dict[str, Any]: The created Reaction resource with the same fields as input, including:
            - name (str): Resource name of the created reaction.
            - emoji (dict):
                - unicode (str): Optional. A basic emoji represented by a unicode string.
                - customEmoji (dict):
                    - name (str): Identifier. Format: customEmojis/{customEmoji}
                    - uid (str): Output only. Unique key for the custom emoji.
                    - emojiName (str): Optional. User-defined emoji name, must be valid format.
                    - temporaryImageUri (str): Output only. Temporary image URL.
                    - payload (dict):
                        - fileContent (str): Required. Image binary data.
                        - filename (str): Required. Image file name (.png, .jpg, .gif).
            - user (dict):
                - name (str): Required. Format: users/{user}
                - displayName (str): Output only. User's display name.
                - domainId (str): Output only. Workspace domain ID.
                - type (str): Enum: TYPE_UNSPECIFIED, HUMAN, BOT
                - isAnonymous (bool): Output only. True if user is deleted or hidden.

        returns empty dict if parent is invalid.
    """
    print_log(f"Reactions.create called with parent={parent}, reaction_body={reaction}")

    # 1) Validate parent format
    parts = parent.split("/")
    if len(parts) < 4 or parts[0] != "spaces" or parts[2] != "messages":
        print_log("Invalid parent format.")
        return {}

    # 2) Generate a reaction name
    new_id = str(len(DB["Reaction"]) + 1)
    reaction_name = f"{parent}/reactions/{new_id}"

    # 3) Build the reaction object
    new_reaction = {
        "name": reaction_name,
        "emoji": reaction.get("emoji", {}),
        "user": reaction.get("user", {}),
    }

    # Insert into DB
    DB["Reaction"].append(new_reaction)
    print_log(f"Created reaction => {new_reaction}")
    return new_reaction


def list(
    parent: str, pageSize: int = None, pageToken: str = None, filter: str = None
) -> Dict[str, Any]:
    """
    Lists reactions to a message.

    Args:
        parent (str): Required. The resource name of the message to list reactions for.
            Format: "spaces/{space}/messages/{message}"
        pageSize (int, optional): Optional. Maximum number of reactions to return. Defaults to 25.
            Maximum value is 200.
        pageToken (str, optional): Optional. Token from a previous list call to retrieve the next page.
        filter (str, optional): Optional. Filter reactions by emoji or user fields. Examples:
            - emoji.unicode = "🙂"
            - emoji.custom_emoji.uid = "XYZ"
            - user.name = "users/USER123"
            - (emoji.unicode = "🙂" OR emoji.unicode = "👍") AND user.name = "users/USER123"

    Returns:
        Dict[str, Any]: A dictionary with the following structure:
            - reactions (list): List of Reaction resources, each including:
                - name (str): Resource name of the reaction.
                - user (dict):
                    - name (str): Resource name of the user.
                    - displayName (str): Output only. User's display name.
                    - domainId (str): Output only. User's domain ID.
                    - type (str): Enum. User type: TYPE_UNSPECIFIED, HUMAN, BOT.
                    - isAnonymous (bool): Output only. Whether the user is anonymous.
                - emoji (dict):
                    - unicode (str): Optional. Unicode emoji.
                    - customEmoji (dict):
                        - name (str): Identifier. Format: customEmojis/{customEmoji}
                        - uid (str): Output only. Unique key.
                        - emojiName (str): Optional. Custom name, must be formatted correctly.
                        - temporaryImageUri (str): Output only. Temporary image URI.
                        - payload (dict):
                            - fileContent (str): Required. Image binary data.
                            - filename (str): Required. File name (.png, .jpg, .gif).
            - nextPageToken (str, optional): Omitted if this is the last page.
    """
    print_log(
        f"Reactions.list called with parent={parent}, pageSize={pageSize}, pageToken={pageToken}, filter={filter}"
    )

    # Default pageSize
    if pageSize is None:
        pageSize = 25
    if pageSize > 200:
        pageSize = 200
    if pageSize < 0:
        pageSize = 25  # or error

    # parse pageToken => offset
    offset = 0
    if pageToken:
        try:
            off = int(pageToken)
            if off >= 0:
                offset = off
        except ValueError:
            pass  # ignore

    # 1) collect all reactions for parent
    all_rxns = []
    for r in DB["Reaction"]:
        if r["name"].startswith(parent + "/reactions/"):
            all_rxns.append(r)

    # 2) apply filter if provided
    # The doc says we can do expressions like:
    #   user.name = "users/USERA" OR user.name = "users/USERB"
    #   emoji.unicode = "🙂" OR emoji.custom_emoji.uid = "XYZ"
    #   AND between user and emoji
    # We'll do a minimal approach:
    def _reaction_matches_filter(rxn: dict, tokens: list) -> bool:
        """
        A minimal parse for filter tokens. For example:
            tokens = ["emoji.unicode", "=", "\"🙂\"", "AND", "user.name", "=", "\"users/USER111\""]
        We'll find expressions of the form [field, "=", quoted_value] and keep track of OR or AND.

        The doc says valid queries:
            user.name = "users/AAAAAA"
            emoji.unicode = "🙂"
            emoji.custom_emoji.uid = "UID"
        We can have OR among the same field type, AND between user and emoji, etc.
        We'll do something extremely naive:
            - We group the tokens into expressions and operators.
            - If an expression is "field = \"value\"", we test rxn's field.

        This won't fully cover parentheses or advanced combos, but demonstrates the concept.
        """
        # We'll parse out expressions of the form (field, "=", value) plus "AND"/"OR" in between.
        expressions = []
        operators = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t.upper() in ("AND", "OR"):
                operators.append(t.upper())
                i += 1
            else:
                # expect something like "field", "=", "\"value\""
                if i + 2 < len(tokens) and tokens[i + 1] == "=":
                    field = tokens[i]
                    val = tokens[i + 2].strip('"')
                    expressions.append((field, val))
                    i += 3
                else:
                    # invalid parse => skip
                    return False

        # We then interpret them in a naive way:
        # - For each expression, check if rxn satisfies it.
        # - If we see "AND", we require both. If we see "OR", we require either. The doc has constraints about grouping.
        # We'll do a simplistic approach:
        if not expressions:
            return True

        # We'll handle them in sequence: expression1 (operator) expression2 (operator) expression3 ...
        # For the doc: "OR" can appear among the same field type, "AND" can appear between different field types
        # We'll apply a partial approach: if any "OR", we treat them as "field matches any of these" if same field, or fail if different.

        # We'll group expressions by field to handle the doc's constraints (only OR within the same field).
        # Then AND across different fields. This is still simplistic but closer to the doc's rules.
        # e.g. user.name = "users/USER111" OR user.name = "users/USER222"
        # AND emoji.unicode = "🙂" OR emoji.unicode = "👍"

        # We'll transform expressions + operators into groups.
        # Example: [("emoji.unicode", "🙂"), OR, ("emoji.unicode", "👍"), AND, ("user.name", "users/USER111")]

        # We'll do a single pass to group by AND:
        groups = []  # each group is a list of expressions that are OR'ed together
        current_group = [expressions[0]]  # start
        for idx, op in enumerate(operators):
            expr = expressions[idx + 1]
            if op == "OR":
                # add to current group
                current_group.append(expr)
            elif op == "AND":
                # finish the current group, start a new group
                groups.append(current_group)
                current_group = [expr]
            else:
                # unknown => skip
                return False
        # add last group
        groups.append(current_group)

        # Now we have groups of OR expressions, we require each group to match (AND).
        # e.g. group1 => [("emoji.unicode","🙂"),("emoji.unicode","👍")] => means rxn must have emoji.unicode that is either "🙂" or "👍"
        # group2 => [("user.name","users/USER111")] => must match as well
        for group in groups:
            # They all share the same field or doc says "OR with same field"? We'll allow them to share the same field or be different, but doc focuses on same field for OR. We'll do an "OR" check among them.
            matched_this_group = False
            for field, val in group:
                if _matches_expression(rxn, field, val):
                    matched_this_group = True
                    break
            if not matched_this_group:
                return False

        return True

    def _matches_expression(rxn: dict, field: str, val: str) -> bool:
        """
        Check if a single reaction satisfies e.g. user.name = "users/USER111"
        or emoji.unicode = "🙂", or emoji.custom_emoji.uid = "ABC".
        """
        if field == "user.name":
            # check rxn["user"]["name"] == val
            return rxn.get("user", {}).get("name") == val
        elif field == "emoji.unicode":
            return rxn.get("emoji", {}).get("unicode") == val
        elif field == "emoji.custom_emoji.uid":
            # rxn["emoji"]["custom_emoji"]["uid"] == val
            return rxn.get("emoji", {}).get("custom_emoji", {}).get("uid") == val
        else:
            # unknown
            return False

    if filter:
        # We'll parse a few patterns for demonstration.
        # Real logic would fully parse parentheses and multiple AND/OR expressions.
        # e.g. "emoji.unicode = \"🙂\" AND user.name = \"users/USER111\""
        # We'll handle basic ( X = "val" ) statements with AND or OR, ignoring parentheses.
        tokens = filter.split()
        # e.g. tokens => ["emoji.unicode", "=", "\"🙂\"", "AND", "user.name", "=", "\"users/USER111\""]
        # We'll do a naive pass
        filtered = []
        for rxn in all_rxns:
            if _reaction_matches_filter(rxn, tokens):
                filtered.append(rxn)
        all_rxns = filtered

    # 3) pagination
    total = len(all_rxns)
    end = offset + pageSize
    page_items = all_rxns[offset:end]
    next_token = None
    if end < total:
        next_token = str(end)

    # Build result
    result = {"reactions": page_items}
    if next_token:
        result["nextPageToken"] = next_token
    return result


def delete(name: str) -> Dict[str, Any]:
    """
    Deletes a reaction by its resource name.

    Args:
        name (str): Required. The resource name of the reaction to delete.
            Format: "spaces/{space}/messages/{message}/reactions/{reaction}"

    Returns:
        Dict[str, Any]: An empty dictionary representing a successful deletion.
    """
    # Find and remove from DB
    for r in DB["Reaction"]:
        if r.get("name") == name:
            DB["Reaction"].remove(r)
            print_log(f"Deleted reaction => {r}")
            return {}
    print_log("Reaction not found => returning {}")
    return {}
