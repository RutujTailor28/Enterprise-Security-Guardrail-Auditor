"""File safety domain rules."""

ALLOWED_EXTENSIONS = {
    ".tf",
    ".tfvars",
    ".tf.json",
    ".json",
    ".yaml",
    ".yml",
    ".template",
}

BLOCKED_EXTENSIONS = {
    ".tfstate",
    ".tfstate.backup",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".env",
    ".exe",
    ".dll",
    ".git",
}

TERRAFORM_EXTENSIONS = {".tf", ".tfvars", ".tf.json"}
CLOUDFORMATION_EXTENSIONS = {".json", ".yaml", ".yml", ".template"}


def get_file_type(filename: str) -> str | None:
    lower = filename.lower()
    if lower.endswith(".tf.json"):
        return "terraform"
    for ext in TERRAFORM_EXTENSIONS:
        if lower.endswith(ext) and ext != ".tf.json":
            return "terraform"
    for ext in CLOUDFORMATION_EXTENSIONS:
        if lower.endswith(ext):
            return "cloudformation"
    return None
