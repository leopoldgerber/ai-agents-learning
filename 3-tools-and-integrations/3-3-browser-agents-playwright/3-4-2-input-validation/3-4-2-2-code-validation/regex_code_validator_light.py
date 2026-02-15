import re


class SimpleCodeValidator:
    """Simple code validation using regular expressions"""

    # Dangerous patterns in code
    DANGEROUS_PATTERNS = [
        (r'\bos\.system\b', 'Use of os.system is forbidden'),
        (r'\beval\b', 'Use of eval() is forbidden'),
        (r'\bexec\b', 'Use of exec() is forbidden'),
        (r'\b__import__\b', 'Direct import via __import__ is forbidden'),
        (r'\bsubprocess\b', 'Use of subprocess is forbidden'),
        (r'\bopen\(.*["\']w["\']', 'File writing is restricted'),
    ]

    # Allowed imports (whitelist)
    ALLOWED_IMPORTS = {
        'math', 'json', 'datetime', 'collections',
        're', 'statistics', 'itertools', 'random'
    }

    @classmethod
    def validate(cls, code: str) -> tuple:
        """
        Checks the code for dangerous constructs.
        Returns (is_valid, error_message)
        """
        # Code length check
        if len(code) > 10000:
            return False, "Code exceeds maximum allowed length"

        # Check for dangerous patterns
        for pattern, message in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Dangerous construct detected: {message}"

        # Check imports
        import_pattern = r'\bimport\s+(\w+)'
        imports = re.findall(import_pattern, code)
        for imp in imports:
            if imp not in cls.ALLOWED_IMPORTS:
                return False, f"Import of module '{imp}' is not allowed"

        return True, None


if __name__ == '__main__':
    # Usage example
    validator = SimpleCodeValidator()

    safe_code = """
        import math
        result = math.sqrt(16)
        print(result)
    """
    is_valid, error = validator.validate(safe_code)
    print(f"Safe code: {is_valid}")

    dangerous_code = """
        import os
        os.system('rm -rf /')
    """
    is_valid, error = validator.validate(dangerous_code)
    print(f"Dangerous code: {is_valid}, reason: {error}")
