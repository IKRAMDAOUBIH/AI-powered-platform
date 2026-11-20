
from module_A.integration.schema import export_for_module_b

input_path = "module_A/data/processed/live_enriched_tenders.json"
output_path = "module_A/data/processed/module_b_tenders.json"

export_for_module_b(input_path, output_path)
