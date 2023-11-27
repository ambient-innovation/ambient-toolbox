# Validators

This package provides additional validators. In the Django ecosystem, you can have two kinds of validators: [Password
validators](https://docs.djangoproject.com/en/4.2/topics/auth/passwords/) and form validators. The first are used in the
settings to add rules for your users passwords. The latter is employed in models and forms to validate user input.

## Auth password validators

### Special characters required

Adding ths validator will require your users to add at least one of the following special characters to their
password: `@#$%!^&*`.

```python
# Django settings

# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    ...
    {
        "NAME": "ambient_toolbox.validators.auth_password.special_chars.SpecialCharValidator",
    },
]

```
