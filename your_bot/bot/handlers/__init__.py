def register_handlers(dp):
    from .rss_handler import register_rss
    from .start import register_start

    register_rss(dp)
    register_start(dp)
