uv run py/validate_lines.py && (
    uv run py/update_config.py
    uv run py/build_data.py
)