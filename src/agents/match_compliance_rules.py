import pandas as pd
import re

EXCEL_RULES_PATH = "data/presaved_rules.xlsx"

def extract_matched_policies(gpt_response_text):
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
                break
    return matched_policies

def extract_rule_id(text):
    match = re.search(r"Rule ID:\s*(\d+)", text)
    return int(match.group(1)) if match else None

def match_with_presaved_rules(gpt_response_text):
    extracted_matched = extract_matched_policies(gpt_response_text)
    if not extracted_matched:
        return {"status": "❌ Could not parse matched policies from compliance agent output."}

    df = pd.read_excel(EXCEL_RULES_PATH)
    print("Excel Columns:", df.columns.tolist())  # Debugging line

    # Try both possible column names
    rule_id_column = "rule_id" if "rule_id" in df.columns else "Rule ID"
    df[rule_id_column] = df[rule_id_column].astype(int)
    df["rule"] = df["rule"].astype(str)

    unmatched_rules = []
    matched = True

    for extracted_rule in extracted_matched:
        rule_id = extract_rule_id(extracted_rule)
        match_row = df[df[rule_id_column] == rule_id]

        if match_row.empty:
            matched = False
            unmatched_rules.append({
                "extracted_rule": extracted_rule,
                "expected_rule": f"No rule found in Excel for Rule ID: {rule_id}"
            })
        else:
            expected_full_rule = match_row["rule"].values[0]
            if extracted_rule != expected_full_rule:
                matched = False
                unmatched_rules.append({
                    "extracted_rule": extracted_rule,
                    "expected_rule": expected_full_rule
                })

    if matched:
        return {"status": "✅ All matched rules align with Excel rules"}
    else:
        return {
            "status": "❌ Mismatched rules found",
            "unmatched_rules": unmatched_rules
        }
