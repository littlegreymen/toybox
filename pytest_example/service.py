from feature_flags import is_feature_enabled

def should_process_request() -> bool:
    """
    Business logic that depends on a feature flag.
    """
    return is_feature_enabled()
