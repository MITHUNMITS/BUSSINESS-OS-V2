from business_os.apps.core.module_registry import load_module_definitions


def test_module_registry_loads_first_release_modules():
    modules = load_module_definitions()

    assert "website" in modules
    assert "catalogue" in modules
    assert "commerce" in modules
    assert "payments" in modules
