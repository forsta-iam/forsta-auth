from idm_auth.daemon import IDMAuthDaemon


if __name__ == '__main__':
    import django
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

    django.setup()
    daemon = IDMAuthDaemon()
    daemon()