import pandas as pd
import json

EXCEL_RULES_PATH = "data/presaved_rules.xlsx"


def extract_matched_policies(gpt_response_text):
    """
    Parses GPT response to extract 'Matched Policies' as a list even from bullet points.
    """
    lines = gpt_response_text.splitlines()
    matched_policies = []
    inside_matched = False

    for line in lines:
        if "Matched Policies" in line:
            inside_matched = True
            continue

        if inside_matched:
            line = line.strip()
            if line.startswith("- Rule ID:"):
                matched_policies.append(line.strip("- ").strip())
            elif line.startswith("- Missing Elements") or line.startswith("- Suggested Clauses"):
                break  # end of matched policies section

    return matched_policies



def match_with_presaved_rules(gpt_response_text):
    extracted_matched = extract_matched_policies(gpt_response_text)
    if not extracted_matched:
        return {"status": "❌ Could not parse matched policies from compliance agent output."}

    df = pd.read_excel(EXCEL_RULES_PATH)
    expected_rules = df["rule"].astype(str).tolist()

    unmatched_rules = []
    matched = True

    for rule in extracted_matched:
        if rule not in expected_rules:
            matched = False
            unmatched_rules.append({
                "extracted_rule": rule,
                "expected_rule": "Not found in Excel"
            })

    if matched:
        return {"status": "✅ All matched rules align with Excel rules"}
    else:
        return {
            "status": "❌ Mismatched rules found",
            "unmatched_rules": unmatched_rules
        }
