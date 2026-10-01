import urllib.request

def test_i18n_served():
    res = urllib.request.urlopen("http://127.0.0.1:8000/static/js/i18n.js")
    assert res.status == 200
    content = res.read().decode("utf-8")
    assert "class I18nManager" in content
    
    # Check that all 6 languages are defined
    for lang in ["en", "hi", "es", "fr", "zh", "de"]:
        assert f"{lang}: {{" in content, f"Missing language block for {lang}"

def test_html_markup():
    res = urllib.request.urlopen("http://127.0.0.1:8000/")
    assert res.status == 200
    html = res.read().decode("utf-8")
    
    # Language selector dropdown
    assert 'id="language-select"' in html
    for opt in ['value="en"', 'value="hi"', 'value="es"', 'value="fr"', 'value="zh"', 'value="de"']:
        assert opt in html, f"Missing option {opt}"
        
    # Script tag
    assert 'src="/static/js/i18n.js"' in html
    
    # Core data-i18n tags
    required_keys = [
        "tagline", "nav_home", "nav_explore", "nav_map", "nav_protocols",
        "nav_packages", "nav_vault", "nav_pricing", "nav_about", "nav_sos",
        "hero_title", "hero_subtitle", "packages_title", "vault_title",
        "pricing_title", "about_title", "footer_rights"
    ]
    for key in required_keys:
        assert f'data-i18n="{key}"' in html, f"Missing data-i18n for key: {key}"

if __name__ == "__main__":
    test_i18n_served()
    print("test_i18n_served PASSED")
    test_html_markup()
    print("test_html_markup PASSED")
