"""Translation module."""
import i18n

i18n.set('filename_format', '{locale}.{format}')
i18n.set('skip_locale_root_data', True)
i18n.load_path.append('./i18n/')
