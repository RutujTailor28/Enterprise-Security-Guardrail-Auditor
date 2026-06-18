"""Parser registry."""

from app.domain.models.parse_result import ParseResult
from app.infrastructure.parsers.cloudformation_parser import CloudFormationParser
from app.infrastructure.parsers.normalizer import normalize_resources
from app.infrastructure.parsers.terraform_parser import TerraformParser

_parsers = [TerraformParser(), CloudFormationParser()]


def parse_file(content: str, filename: str) -> ParseResult:
    for parser in _parsers:
        if parser.can_parse(filename):
            result = parser.parse(content, filename)
            result.resources = normalize_resources(result.resources)
            return result
    return ParseResult(errors=[f"No parser available for file '{filename}'"])
