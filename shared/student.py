STUDENT_NAME  = "Кохманський Михайло Михайлович"
GROUP_NAME = "КБ-203"
VARIANT_NUMBER = 11

passwords = ["APT@Detect10n", "simple", "Red@Team2023", "participant", "BLue@T3am", "common123", "Purple@T34m", "regular123", "Gr33n@Team", "normal123"]
criteria = {"min_length": 7, "require_digits": True, "require_upper": True, "require_special": True}
forbidden_passwords = {"simple", "participant", "common123", "regular123", "normal123", "test"}


users = {
    "risk_manager": {"role": "risk_analyst", "clearance": 4, "department": "Risk Management", "active": True},
    "business_analyst": {"role": "business_analyst", "clearance": 2, "department": "Business", "active": True},
    "legal_counsel": {"role": "legal", "clearance": 3, "department": "Legal", "active": True},
    "contractor_dev": {"role": "contractor", "clearance": 2, "department": "Contract", "active": True},
    "obsolete_system": {"role": "legacy_system", "clearance": 1, "department": "Legacy", "active": False},
}

resources = [("risk_registers", 4), ("business_requirements", 2), ("legal_documents", 3), ("contract_code", 2), ("governance_framework", 4), ("meeting_minutes", 1), ("regulatory_reports", 3), ("executive_dashboards", 4), ("project_specs", 2), ("public_statements", 1)]
security_levels = ("Public", "Internal Use", "Restricted", "Highly Restricted")
blocked_users = {"obsolete_system", "contract_expired", "legal_hold"}
