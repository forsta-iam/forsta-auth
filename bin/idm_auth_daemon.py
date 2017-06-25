

if __name__ == '__main__':
    import django
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

    django.setup()

    from idm_auth.daemon import IDMAuthDaemon
    daemon = IDMAuthDaemon()
    daemon()