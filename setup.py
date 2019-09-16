import os.path
import re
import setuptools

with open('README.md') as f:
    long_description = f.read()

with open(os.path.join('forsta_auth', '__init__.py')) as f:
    version = re.search(
        r'''^__version__\s*=\s*(['"])(.*)\1''', f.read(), re.MULTILINE
    ).group(2)

setuptools.setup(
    name='forsta-auth',
    version=version,
    author='Alexander Dutton',
    author_email='forsta@alexdutton.co.uk',
    description='A federated authentication service',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/forsta-iam/forsta-auth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django :: 2.2",
        "Topic :: Internet :: WWW/HTTP",
    ],
    install_requires=[
        "celery",
        "Django",
        "djangorestframework",
        "django-reversion",
        "django-zxcvbn-password",
        "requests",
        "social-auth-app-django",
        "django-otp",
        "django-two-factor-auth",
        "django-registration",
        "django-oidc-provider",
        "django-dirtyfields",
        "django-templated-email",
        "django-cors-headers",
    ],
    extras_require={
        "kerberos": ["pykerberos", "requests-negotiate"],
        "saml": ["xmlsec", "python3-saml"],
        "environ": ["django-environ"],
    },
)
