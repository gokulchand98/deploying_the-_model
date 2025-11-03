def test_smoke_import():
    import importlib
    m = importlib.import_module('app.agent')
    assert hasattr(m, 'search_jobs')
    assert hasattr(m, 'generate_cover_letter_sync')
